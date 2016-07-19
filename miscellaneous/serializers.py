from rest_framework import serializers
from .models import *


class TaxReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxReceipt
        fields = '__all__'

        extra_kwargs = {
            'user': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['user']
        obj = TaxReceipt.objects.create(**validated_data)
        return obj
