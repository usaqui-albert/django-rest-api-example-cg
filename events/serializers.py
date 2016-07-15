from rest_framework import serializers
from .models import *


class EventSerializer(serializers.ModelSerializer):
    """Serializer to handle requests and response of the event attributes"""
    class Meta:
        model = Event
        fields = '__all__'
