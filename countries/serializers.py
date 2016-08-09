from rest_framework import serializers
from .models import *


class CountrySerializer(serializers.ModelSerializer):
    """Serializer to handle requests and response of the Country attributes"""
    class Meta:
        model = Country
        fields = ('id', 'name', 'created_at')
