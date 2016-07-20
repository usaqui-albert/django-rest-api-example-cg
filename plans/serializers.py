from rest_framework import serializers


class SubscriptionSerializer(serializers.Serializer):
    plan_id = serializers.CharField(max_length=100)
