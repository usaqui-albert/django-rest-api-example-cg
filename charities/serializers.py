from rest_framework import serializers

from .models import *


class CharityCategorySerializer(serializers.ModelSerializer):
    charities = serializers.SerializerMethodField()

    class Meta:
        model = CharityCategory
        fields = '__all__'

    def get_charities(self, instance):
        charities = self.context['charities']
        if 'country_id' in self.context:
            queryset = charities.filter(country=self.context['country_id'], charity=instance.id)
        else:
            queryset = charities
        serializer = CharityCountrySerializer(queryset, many=True)
        return serializer.data


class CharityCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CharityCountry
        fields = ('id', 'name', 'created_at', 'updated_at')
