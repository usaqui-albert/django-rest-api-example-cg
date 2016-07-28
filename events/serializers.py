from rest_framework import serializers

from .models import Event
from countries.serializers import CountrySerializer
from charities.serializers import CharityCategorySerializer
from charities.models import CharityCategory, CharityCountry


class CreateEventSerializer(serializers.ModelSerializer):
    """Serializer to handle requests and responses of the event attributes when a event
     is created
     """
    class Meta:
        """Relating to an Event model and including all fields"""
        model = Event
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    """Serializer to get or update events handling requests and responses of its attributes"""
    country = serializers.SerializerMethodField()
    charities_by_category = serializers.SerializerMethodField()

    class Meta:
        """Relating to an Event model and including all fields"""
        model = Event
        fields = '__all__'

    @staticmethod
    def get_country(instance):
        """Method to specify the value of country attribute

        :param instance: event object
        :return: country object serialized
        """
        return CountrySerializer(instance.country).data

    @staticmethod
    def get_charities_by_category(instance):
        """Method to specify the value of charities_by_category attribute

        :param instance: event object
        :return: charities objects serialized and populated by charity categories
        """
        charities_by_category = CharityCategory.objects.all()
        charities_by_country = CharityCountry.objects.all()
        context = {
            'country_id': instance.country.id,
            'charities': charities_by_country
        }
        serializer = CharityCategorySerializer(charities_by_category, many=True, context=context)
        return serializer.data
