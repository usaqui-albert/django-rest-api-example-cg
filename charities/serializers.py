from rest_framework import serializers

from .models import CharityCategory, CharityCountry


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
        serializer = CharityCountrySerializer(queryset, many=True)
        return serializer.data


class CharityCountrySerializer(serializers.ModelSerializer):
    """Serializer to get the detail of a charity"""
    class Meta:
        """Relating to the CharityCountry model and excluding country and category field"""
        model = CharityCountry
        fields = ('id', 'name', 'created_at', 'updated_at')
