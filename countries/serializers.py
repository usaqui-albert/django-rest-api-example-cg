from rest_framework import serializers
from .models import *

from states.serializers import StateSerializer


class CountrySerializer(serializers.ModelSerializer):
    """Serializer to handle requests and response of the Country attributes"""
    states = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(CountrySerializer, self).__init__(*args, **kwargs)
        if 'without_states' in self.context:
            self.fields.pop('states')

    class Meta:
        model = Country
        fields = ('id', 'name', 'created_at', 'states')

    @staticmethod
    def get_states(instance):
        serializer = StateSerializer(instance.states, many=True)
        return serializer.data
