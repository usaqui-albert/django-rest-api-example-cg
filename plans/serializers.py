from rest_framework import serializers
from .models import PromoCode


class SubscriptionSerializer(serializers.Serializer):
    plan_id = serializers.CharField(max_length=100)

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'
        extra_kwargs = {
            'used': {'read_only': True}
        }
