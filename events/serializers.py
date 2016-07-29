from rest_framework import serializers

from .models import Event
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
    charities_by_category = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()

    class Meta:
        """Relating to an Event model and including all fields"""
        model = Event
        fields = '__all__'

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

    @staticmethod
    def get_status(instance):
        user_event = instance.user_event.get()
        return user_event.get_status_as_string()

    @staticmethod
    def get_sender(instance):
        user_event = instance.user_event.get()
        return user_event.user.get_full_name()


STATUS_OF_THE_EVENT = (('ACCEPTED', 'A'), ('REJECTED', 'R'))

class AcceptOrRejectEventSerializer(serializers.Serializer):
    charity = serializers.IntegerField(min_value=1)
    status = serializers.ChoiceField(choices=STATUS_OF_THE_EVENT)
    key = serializers.CharField(max_length=100)
