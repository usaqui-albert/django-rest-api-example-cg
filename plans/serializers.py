from rest_framework import serializers
from users.models import User
from countries.serializers import CountrySerializer
from states.serializers import StateSerializer


class UserDataSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('pk', 'email', 'street_address', 'city', 'province', 'country', 'zip_code')

    @staticmethod
    def get_country(instance):
        """

        :param instance:
        :return:
        """
        return CountrySerializer(instance.country).data

    @staticmethod
    def get_province(instance):
        """

        :param instance:
        :return:
        """
        return StateSerializer(instance.province).data
