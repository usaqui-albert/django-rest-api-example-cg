from rest_framework import serializers
from .models import *

class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer to create a new user"""

    terms_conditions = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        exclude = ['']
        extra_kwargs = {
            'password': {'write_only': True},
            'pk': {'read_only': True}
        }

    def create(self, validated_data):
        del validated_data['terms_conditions']
        obj = User.objects.create(**validated_data)

        obj.set_password(obj.password)
        obj.save()
        self.fields.pop('first_name')
        self.fields.pop('last_name')
        self.fields.pop('direction')
        self.fields.pop('phone_number')
        return obj

    def validate_terms_conditions(self, value):
        if not value:
            raise serializers.ValidationError("You must accept terms and conditions")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = []
