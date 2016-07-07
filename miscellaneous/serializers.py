from rest_framework import serializers
from .models import *


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'


class LandingTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'


class TaxReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxReceipt
        fields = '__all__'
