import stripe
from stripe.error import InvalidRequestError, APIConnectionError, CardError

from rest_framework import serializers
from django.db import IntegrityError

from .models import User
from miscellaneous.models import CustomerStripe
from ConnectGood.settings import STRIPE_API_KEY
from miscellaneous.helpers import card_list, stripe_errors_handler
from plans.helpers import get_plans_list_response
from countries.serializers import CountrySerializer
from states.serializers import StateSerializer


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer to create a new user"""
    terms_conditions = serializers.BooleanField(write_only=True)
    card_token = serializers.CharField(max_length=100)
    plan_id = serializers.CharField(max_length=100)
    is_corporate_account = serializers.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(CreateUserSerializer, self).__init__(*args, **kwargs)
        stripe.api_key = STRIPE_API_KEY

    class Meta:
        """Relating to a User model and customizing the serializer fields"""
        model = User
        fields = (
            'email', 'password', 'first_name', 'last_name', 'company', 'street_address',
            'country', 'city', 'phone_number', 'terms_conditions', 'card_token', 'plan_id',
            'province', 'is_corporate_account', 'zip_code', 'pk'
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
        plan_id = validated_data.pop('plan_id')
        card_token = validated_data.pop('card_token')
        is_corporate_account = bool(validated_data.pop('is_corporate_account'))

        try:
            customer = stripe.Customer.create(
                description='Customer for ' + validated_data['email'],
                source=card_token,
                email=validated_data['email'],
                plan=plan_id
            )
        except (APIConnectionError, InvalidRequestError, CardError) as e:
            raise serializers.ValidationError(stripe_errors_handler(e))
        else:
            validated_data['tax_receipts_as'] = 2 if is_corporate_account else 1
            user = create_user_hashing_password(**validated_data)
            if not user:
                raise serializers.ValidationError('There was an Integrity Error creating a user')
            CustomerStripe.objects.create(user=user, customer_id=customer.id)
            return user

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


class UserSerializer(serializers.ModelSerializer):
    """Serializer to update or get a user information"""
    payment_method = serializers.SerializerMethodField()
    tax_receipts_as = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    is_corporate_account = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        if 'without_payment' in self.context:
            self.fields.pop('payment_method')
        if 'without_plan' in self.context:
            self.fields.pop('plan')
        stripe.api_key = STRIPE_API_KEY
        self.customer = None

    class Meta:
        """Relating to a User model and excluding password field"""
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'company', 'street_address', 'country',
            'city', 'phone_number', 'has_a_plan', 'created_at', 'updated_at', 'province',
            'tax_receipts_as', 'payment_method', 'zip_code', 'is_corporate_account', 'pk',
            'is_active', 'plan'
        )
        extra_kwargs = {
            'pk': {'read_only': True},
            'has_a_plan': {'read_only': True},
            'payment_method': {'read_only': True},
            'plan': {'read_only': True},
            'tax_receipts_as': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'is_active': {'read_only': True}
        }

    def get_payment_method(self, instance):
        if instance.has_a_plan:
            if self.customer is None:
                customer = get_customer_in_stripe(instance)
                if isinstance(customer, str):
                    raise serializers.ValidationError(customer)
                self.customer = customer
            cards_response = self.customer.sources.data
            return card_list(cards_response)[0]
        else:
            return None

    def get_plan(self, instance):
        if instance.has_a_plan:
            if self.customer is None:
                customer = get_customer_in_stripe(instance)
                if isinstance(customer, str):
                    raise serializers.ValidationError(customer)
                self.customer = customer
            plan = self.customer.subscriptions.data[0]['plan']
            return get_plans_list_response([plan])[0]
        else:
            return None

    @staticmethod
    def get_tax_receipts_as(instance):
        return instance.get_tax_receipts_as_string()

    @staticmethod
    def get_country(instance):
        return CountrySerializer(instance.country).data

    @staticmethod
    def get_province(instance):
        return StateSerializer(instance.province).data

    @staticmethod
    def get_is_corporate_account(instance):
        return instance.is_corporate_account()


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
        user.has_a_plan = True
        user.save()
    except IntegrityError:
        return False
    return user

def get_customer_in_stripe(instance):
    customer_stripe = CustomerStripe.objects.filter(user=instance.id)
    if customer_stripe.exists():
        try:
            customer = stripe.Customer.retrieve(customer_stripe.first().customer_id)
        except (APIConnectionError, InvalidRequestError, CardError) as err:
            error = stripe_errors_handler(err)
        else:
            return customer
    else:
        error = "There is no stripe customer available for this user"
    return error


class UpdateUserSerializer(serializers.ModelSerializer):
    card_token = serializers.CharField(max_length=100, allow_null=True)
    plan_id = serializers.CharField(max_length=100, allow_null=True)
    is_corporate_account = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = (
            'pk', 'email', 'first_name', 'last_name', 'company', 'country', 'city', 'province',
            'phone_number', 'zip_code', 'is_active', 'street_address', 'password', 'plan_id',
            'card_token', 'is_corporate_account'
        )
        extra_kwargs = {
            'pk': {'read_only': True},
            'password': {'write_only': True}
        }

    def __init__(self, *args, **kwargs):
        super(UpdateUserSerializer, self).__init__(*args, **kwargs)
        if 'without_card' in self.context:
            self.fields.pop('card_token')
        if 'without_plan' in self.context:
            self.fields.pop('plan_id')
        stripe.api_key = STRIPE_API_KEY

    def update(self, instance, validated_data):
        """

        :param instance:
        :param validated_data:
        :return:
        """
        if 'card_token' in validated_data or 'plan_id' in validated_data:
            customer = get_customer_in_stripe(instance)
            if isinstance(customer, str):
                raise serializers.ValidationError(customer)
            if 'card_token' in validated_data and 'plan_id' not in validated_data:
                card_token = validated_data.pop('card_token')
                res = self.update_payment_method(customer, card_token)
                if isinstance(res, str):
                    raise serializers.ValidationError(res)
            elif 'plan_id' in validated_data and 'card_token' not in validated_data:
                plan_id = validated_data.pop('plan_id')
                res = self.update_subscription_plan(customer, plan_id)
                if isinstance(res, str):
                    raise serializers.ValidationError(res)
            elif 'card_token' in validated_data and 'plan_id' in validated_data:
                card_token = validated_data.pop('card_token')
                plan_id = validated_data.pop('plan_id')
                card_res = self.update_payment_method(customer, card_token)
                if isinstance(card_res, str):
                    raise serializers.ValidationError(card_res)
                plan_res = self.update_subscription_plan(customer, plan_id)
                if isinstance(plan_res, str):
                    raise serializers.ValidationError(card_res)
        self.fields.pop('plan_id', None)
        self.fields.pop('card_token', None)
        if 'is_corporate_account' in validated_data:
            is_corporate_account = bool(validated_data.pop('is_corporate_account'))
            validated_data['tax_receipts_as'] = 2 if is_corporate_account else 1
        return super(UpdateUserSerializer, self).update(instance, validated_data)

    @staticmethod
    def update_payment_method(customer, card_token):
        customer.source = card_token
        try:
            customer.save()
        except (APIConnectionError, InvalidRequestError, CardError) as err:
            return stripe_errors_handler(err)
        else:
            return customer

    @staticmethod
    def update_subscription_plan(customer, plan_id):
        subscription_id = str(customer.subscriptions.data[0].id)
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
        except (APIConnectionError, InvalidRequestError, CardError) as err:
            return stripe_errors_handler(err)
        else:
            subscription.plan = plan_id
            try:
                subscription.save()
            except (APIConnectionError, InvalidRequestError, CardError) as err:
                return stripe_errors_handler(err)
            else:
                return subscription
