import stripe

from rest_framework import serializers
from .models import User
from miscellaneous.models import CustomerStripe
from ConnectGood.settings import STRIPE_API_KEY

class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer to create a new user"""
    terms_conditions = serializers.BooleanField(write_only=True)
    card_token = serializers.CharField(max_length=100)
    plan_id = serializers.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        super(CreateUserSerializer, self).__init__(*args, **kwargs)
        stripe.api_key = STRIPE_API_KEY

    class Meta:
        """Relating to a User model and customizing the serializer fields"""
        model = User
        fields = (
            'email', 'password', 'first_name', 'last_name', 'company', 'street_address',
            'country', 'city', 'phone_number', 'terms_conditions', 'card_token', 'plan_id', 'pk'
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
        card_token = validated_data.pop('card_token')
        plan_id = validated_data.pop('plan_id')
        self.fields.pop('plan_id')
        self.fields.pop('card_token')
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
            user = User.objects.create(**validated_data)
            user.set_password(user.password)
            user.save()
            CustomerStripe.objects.create(user=user, customer_id=customer.id)
            return user

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
