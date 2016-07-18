from rest_framework import serializers

from .models import *
from countries.serializers import CountrySerializer
from miscellaneous.serializers import TaxReceiptSerializer
from charities.serializers import CharityCategorySerializer
from charities.models import *


class CreateEventSerializer(serializers.ModelSerializer):
    """Serializer to handle requests and response of the event attributes"""
    class Meta:
        model = Event
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    tax_receipt = serializers.SerializerMethodField()
    charities_by_category = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    @staticmethod
    def get_country(instance):
        return CountrySerializer(instance.country).data

    @staticmethod
    def get_tax_receipt(instance):
        tax = instance.tax_receipt
        return TaxReceiptSerializer(tax).data if tax else tax

    @staticmethod
    def get_charities_by_category(instance):
        charities_by_category = CharityCategory.objects.all()
        charities_by_country = CharityCountry.objects.all()
        context = {
            'country_id': instance.country.id,
            'charities': charities_by_country
        }
        serializer = CharityCategorySerializer(charities_by_category, many=True, context=context)
        return serializer.data
