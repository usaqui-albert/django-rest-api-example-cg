from rest_framework import serializers

from .models import Event
from charities.serializers import CharityCategorySerializer
from charities.models import CharityCategory, CharityCountry
from .helpers import validate_uuid4, STATUS_OF_THE_EVENT


class CreateEventSerializer(serializers.ModelSerializer):
    """Serializer to handle requests and responses of the event attributes when a event
     is created
     """
    class Meta:
        """Relating to an Event model and including all fields"""
        model = Event
        fields = '__all__'
        extra_kwargs = {
            'company': {'allow_blank': True}
        }


class EventSerializer(serializers.ModelSerializer):
    """Serializer to get or update events handling requests and responses of its attributes"""
    charities_by_category = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    recipient_name = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(EventSerializer, self).__init__(*args, **kwargs)
        if 'host' not in self.context:
            self.fields.pop('charities_by_category')
        if 'without_sender' in self.context:
            self.fields.pop('sender')

    class Meta:
        """Relating to an Event model and including all fields"""
        model = Event
        fields = '__all__'

    def get_charities_by_category(self, instance):
        """Method to specify the value of charities_by_category attribute

        :param instance: event object
        :return: charities objects serialized and populated by charity categories
        """
        charities_by_category = CharityCategory.objects.all()
        charities_by_country = CharityCountry.objects.all()
        context = {
            'country_id': instance.country.id,
            'charities': charities_by_country,
            'host': self.context['host']
        }
        serializer = CharityCategorySerializer(charities_by_category, many=True, context=context)
        return serializer.data

    @staticmethod
    def get_status(instance):
        user_event = instance.user_event.first()
        return user_event.get_status_as_string()

    @staticmethod
    def get_sender(instance):
        user = instance.user_event.first().user
        return str(user.company) if user.is_corporate_account() else user.get_full_name()

    @staticmethod
    def get_recipient_name(instance):
        return str(instance.recipient_name).split(' ')[0]


class AcceptOrRejectEventSerializer(serializers.Serializer):
    charity_name = serializers.CharField(max_length=255, required=False)
    charity = serializers.CharField(max_length=100, required=False)
    status = serializers.ChoiceField(choices=STATUS_OF_THE_EVENT)
    key = serializers.CharField(max_length=100)

    @staticmethod
    def validate_key(value):
        if not validate_uuid4(value):
            raise serializers.ValidationError('Invalid key')
        return value
