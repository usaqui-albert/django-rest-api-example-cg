from rest_framework import serializers
from .models import State


class StateSerializer(serializers.ModelSerializer):
    """Serializer to handle requests and response of the Country attributes"""
    class Meta:
        """Relating to a State model and including all fields"""
        model = State
        exclude = ['country']
