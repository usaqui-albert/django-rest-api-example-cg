import stripe

from rest_framework import serializers
from django.db import IntegrityError

from .models import User
from plans.models import PromoCode
from miscellaneous.models import CustomerStripe
from ConnectGood.settings import STRIPE_API_KEY
from miscellaneous.helpers import card_list


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer to create a new user"""
    terms_conditions = serializers.BooleanField(write_only=True)
    card_token = serializers.CharField(max_length=100, allow_null=True, required=False)
    plan_id = serializers.CharField(max_length=100, allow_null=True, required=False)
    promo_code = serializers.CharField(max_length=100, required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        super(CreateUserSerializer, self).__init__(*args, **kwargs)
        stripe.api_key = STRIPE_API_KEY

    class Meta:
        """Relating to a User model and customizing the serializer fields"""
        model = User
        fields = (
            'email', 'password', 'first_name', 'last_name', 'company', 'street_address',
            'country', 'city', 'phone_number', 'terms_conditions', 'card_token', 'plan_id',
            'promo_code', 'province', 'tax_receipts_as', 'zip_code', 'pk'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'pk': {'read_only': True}
        }

    def create(self, validated_data):
        """Method rewrote to customize the creation of a user and handling stripe exceptions

        :param validated_data: request(dict) already validated
        :except: message of invalid request error when hitting stripe api
        :return: user object created
        """
        del validated_data['terms_conditions']
        if 'promo_code' in validated_data:
            validated_data.pop('plan_id', None)
            validated_data.pop('card_token', None)
            promo_code = validated_data.pop('promo_code')
            user = create_user_hashing_password(**validated_data)
            if not user:
                raise serializers.ValidationError('There was an Integrity Error creating a user')
            promo_code.update(used=True)
            user.start_free_trial()
            user.save()
            return user
        elif 'plan_id' in validated_data and 'card_token' in validated_data:
            plan_id = validated_data.pop('plan_id')
            card_token = validated_data.pop('card_token')
            try:
                customer = stripe.Customer.create(
                    description='Customer for ' + validated_data['email'],
                    source=card_token,
                    email=validated_data['email'],
                    plan=plan_id
                )
            except stripe.error.InvalidRequestError as e:
                body = e.json_body
                return body['error']['message']
            else:
                user = create_user_hashing_password(**validated_data)
                user.has_a_plan = True
                user.save()
                if not user:
                    raise serializers.ValidationError('There was an Integrity Error creating a user')
                CustomerStripe.objects.create(user=user, customer_id=customer.id)
                return user
        else:
            raise serializers.ValidationError(
                'If there is no promo code you have to send Plan and Card fields'
            )

    @staticmethod
    def validate_terms_conditions(value):
        """Method to validate terms_conditions field, if it is null raises a validation
        error message

        :param value: value of the terms_conditions field
        :raise: message of validation error for this field
        :return: validated value
        """
        if not value:
            raise serializers.ValidationError("You must accept terms and conditions")
        return value

    def validate_card_token(self, value):
        """Method to validate card_token field, if there is an error raises a validation error
        message

        :param value: value of card_token field
        :raise: message of validation error if there is no plan_id key
        :return: validated value
        """
        if 'plan_id' not in self.get_initial():
            raise serializers.ValidationError("This field is allowed only if exists a Plan field")
        if not value and 'promo_code' not in self.get_initial():
            raise serializers.ValidationError("This field can not be blank")
        return value

    def validate_plan_id(self, value):
        """Method to validate plan_id field, if there is an error raises a validation error
        message

        :param value: value of the plan_id field
        :raise: message of validation error if there is no card_token key
        :return: validated value
        """
        if 'card_token' not in self.get_initial():
            raise serializers.ValidationError("This field is allowed only if exists a Card field")
        if not value and 'promo_code' not in self.get_initial():
            raise serializers.ValidationError("This field can not be blank")
        return value

    @staticmethod
    def validate_promo_code(value):
        """Method to validate promo_code field, if there is an error raises a validation error
        message

        :param value: value of the promo_code field
        :raise: message of validation error if promo_code key exists and it is empty
        :return: django filter object with promo code object in it
        """
        if not value:
            raise serializers.ValidationError("This field can not be blank")
        promo_code_stored = PromoCode.objects.filter(code=value)
        if not promo_code_stored.exists():
            raise serializers.ValidationError("This promo code does not exists")
        if promo_code_stored.first().used:
            raise serializers.ValidationError("This promo code is already used")
        return promo_code_stored


class UserSerializer(serializers.ModelSerializer):
    """Serializer to update or get a user information"""
    payment_method = serializers.SerializerMethodField()
    tax_receipts_as = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        stripe.api_key = STRIPE_API_KEY

    class Meta:
        """Relating to a User model and excluding password field"""
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'company', 'street_address', 'country',
            'city', 'phone_number', 'has_a_plan', 'free_trial_started_at', 'created_at',
            'updated_at', 'province', 'tax_receipts_as', 'payment_method', 'pk'
        )
        extra_kwargs = {
            'pk': {'read_only': True},
            'has_a_plan': {'read_only': True},
            'free_trial_started_at': {'read_only': True},
            'payment_method': {'read_only': True},
            'tax_receipts_as': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    @staticmethod
    def get_payment_method(instance):
        if instance.has_a_plan:
            customer_stripe = CustomerStripe.objects.filter(user=instance.id)
            if not customer_stripe.exists():
                raise serializers.ValidationError("There is no stripe customer available for this user")
            customer = stripe.Customer.retrieve(customer_stripe.first().customer_id)
            cards_response = customer.sources.all(limit=3, object='card')
            return card_list(cards_response.data)[0]
        else:
            return None

    @staticmethod
    def get_tax_receipts_as(instance):
        return instance.get_tax_receipts_as_string()


def create_user_hashing_password(**validated_data):
    """Helper method function to create a new user, hash its password and store it in the database

    :param validated_data: request dictionary did by the user
    :except: if there is an integrity error the method return False
    :return: user object if the user was successfully created
    """
    try:
        user = User.objects.create(**validated_data)
        user.set_password(user.password)
        user.is_active = True
        user.save()
    except IntegrityError:
        return False
    return user
