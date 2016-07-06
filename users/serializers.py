from rest_framework import serializers
from .models import *

class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer to create a new user"""
    terms_conditions = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'password', 'first_name', 'last_name', 'company', 'street_address',
            'country', 'city', 'phone_number', 'terms_conditions', 'pk'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'pk': {'read_only': True}
        }

    def create(self, validated_data):
        del validated_data['terms_conditions']
        obj = User.objects.create(**validated_data)
        obj.set_password(obj.password)
        obj.save()
        return obj

    def validate_terms_conditions(self, value):
        if not value:
            raise serializers.ValidationError("You must accept terms and conditions")
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializer to update or get a user information"""
    class Meta:
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
