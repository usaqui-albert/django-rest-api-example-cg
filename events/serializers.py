from rest_framework import serializers

from .models import *
from countries.serializers import CountrySerializer


class CreateEventSerializer(serializers.ModelSerializer):
    """Serializer to handle requests and response of the event attributes"""
    class Meta:
        model = Event
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    @staticmethod
    def get_country(instance):
        obj = instance.country
        serializer = CountrySerializer(obj)
        return serializer.data

    @staticmethod
    def get_tax_receipt(instance):
        return instance.tax_receipt
