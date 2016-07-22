import stripe

from rest_framework import serializers
from django.db import IntegrityError

from .models import User
from plans.models import PromoCode
from miscellaneous.models import CustomerStripe
from ConnectGood.settings import STRIPE_API_KEY


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
            'promo_code', 'province', 'pk'
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
            del validated_data['promo_code']
            user = create_user_hashing_password(**validated_data)
            user.start_free_trial()
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
                if isinstance(user, User):
                    CustomerStripe.objects.create(user=user, customer_id=customer.id)
                    return user
                raise serializers.ValidationError('There was an Integrity Error creating a user')
        else:
            raise serializers.ValidationError('If there is no promo code you have to send Plan and Card fields')

    @staticmethod
    def validate_terms_conditions(value):
        """Method to validate the value of terms_conditions field

        :param: value of the terms_conditions field
        :raise: message of validation error for this field
        :return: validated value
        """
        if not value:
            raise serializers.ValidationError("You must accept terms and conditions")
        return value

    def validate_card_token(self, value):
        """

        :param value:
        :return:
        """
        if 'plan_id' not in self.get_initial():
            raise serializers.ValidationError("This field is allowed only if exists a Plan field")
        if not value and 'promo_code' not in self.get_initial():
            raise serializers.ValidationError("This field can not be blank")
        return value

    def validate_plan_id(self, value):
        """

        :param value:
        :return:
        """
        if 'card_token' not in self.get_initial():
            raise serializers.ValidationError("This field is allowed only if exists a Card field")
        if not value and 'promo_code' not in self.get_initial():
            raise serializers.ValidationError("This field can not be blank")
        return value

    @staticmethod
    def validate_promo_code(value):
        """

        :param value:
        :return:
        """
        if not value:
            raise serializers.ValidationError("This field can not be blank")
        promo_code_stored = PromoCode.objects.filter(code=value)
        if not promo_code_stored.exists():
            raise serializers.ValidationError("This promo code does not exists")
        if promo_code_stored.get().used:
            raise serializers.ValidationError("This promo code is already used")
        promo_code_stored.update(used=True)
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer to update or get a user information"""

    class Meta:
        """Relating to a User model and excluding password field"""
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'company', 'street_address', 'country',
            'city', 'phone_number', 'has_a_plan', 'free_trial_started_at', 'created_at',
            'updated_at', 'pk'
        )
        extra_kwargs = {
            'pk': {'read_only': True},
            'has_a_plan': {'read_only': True},
            'free_trial_started_at': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

def create_user_hashing_password(**validated_data):
    print validated_data
    try:
        user = User.objects.create(**validated_data)
        user.set_password(user.password)
        user.is_active = True
        user.save()
    except IntegrityError:
        return False
    return user
