from rest_framework import serializers

from .models import CharityCategory, CharityCountry
from ConnectGood.settings import MEDIA_URL
from events.helpers import validate_uuid4


class CharityCategorySerializer(serializers.ModelSerializer):
    """Serializer to get all charities populated by categories"""
    charities = serializers.SerializerMethodField()

    class Meta:
        """Relating to the CharityCategory model and including all fields"""
        model = CharityCategory
        fields = '__all__'

    def get_charities(self, instance):
        """Method to get the charities filter by country and a charity category

        :param instance: charity category object
        :return: charities filter by country and the current category instance
        """
        charities = self.context['charities']
        if 'country_id' in self.context:
            queryset = charities.filter(country=self.context['country_id'], charity=instance.id)
        else:
            queryset = charities
        serializer = CharityCountrySerializer(queryset, many=True, context={'host': self.context['host']})
        return serializer.data


class CharityCountrySerializer(serializers.ModelSerializer):
    """Serializer to get the detail of a charity"""
    picture = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(CharityCountrySerializer, self).__init__(*args, **kwargs)
        if 'host' not in self.context:
            self.fields.pop('picture')

    class Meta:
        """Relating to the CharityCountry model and excluding country and category field"""
        model = CharityCountry
        fields = ('id', 'name', 'picture', 'created_at', 'updated_at')

    def get_picture(self, instance):
        return self.context['host'] + MEDIA_URL + instance.get_path_picture()

    @staticmethod
    def get_id(instance):
        return instance.benevity_id


class SearchCharitySerializer(serializers.Serializer):
    term = serializers.CharField(max_length=255)
    key = serializers.CharField(max_length=100)

    @staticmethod
    def validate_key(value):
        if not validate_uuid4(value):
            raise serializers.ValidationError('Invalid key')
        return value
