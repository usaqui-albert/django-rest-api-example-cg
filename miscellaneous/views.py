from rest_framework import generics, permissions

from .serializers import *
from .models import *


class PaymentMethodView(generics.ListCreateAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = (permissions.AllowAny,)


class PaymentMethodDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = (permissions.AllowAny,)


class LandingTemplateView(generics.ListCreateAPIView):
    queryset = Template.objects.all()
    serializer_class = LandingTemplateSerializer
    permission_classes = (permissions.AllowAny,)


class LandingTemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Template.objects.all()
    serializer_class = LandingTemplateSerializer
    permission_classes = (permissions.AllowAny,)


class TaxReceiptView(generics.ListCreateAPIView):
    queryset = TaxReceipt.objects.all()
    serializer_class = TaxReceiptSerializer
    permission_classes = (permissions.AllowAny,)


class TaxReceiptDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TaxReceipt.objects.all()
    serializer_class = TaxReceiptSerializer
    permission_classes = (permissions.AllowAny,)
