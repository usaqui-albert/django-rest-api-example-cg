import stripe

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from .serializers import *
from .models import *
from .helpers import card_list
from ConnectGood.settings import STRIPE_API_KEY


class PaymentMethodView(generics.GenericAPIView):
    """Service to add a new card to the customer in stripe that belong to the user

    :accepted methods:
        POST
        GET
    """
    def __init__(self, *args, **kwargs):
        super(PaymentMethodView, self).__init__(*args, **kwargs)
        stripe.api_key = STRIPE_API_KEY

    serializer_class = LandingTemplateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        customer_stripe = get_object_or_404(CustomerStripe, user=request.user.id)
        customer = stripe.Customer.retrieve(customer_stripe.customer_id)
        customer.sources.create(source=request.data["card_token"])
        return Response(status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        customer_stripe = get_object_or_404(CustomerStripe, user=request.user.id)
        customer = stripe.Customer.retrieve(customer_stripe.customer_id)
        cards_response = customer.sources.all(limit=3, object='card')
        return Response(card_list(cards_response.data))


class LandingTemplateView(generics.ListCreateAPIView):
    """Service to create a new landing template or get all of them(temporary)

    :accepted methods:
        POST
        GET
    """
    queryset = Template.objects.all()
    serializer_class = LandingTemplateSerializer
    permission_classes = (permissions.AllowAny,)


class LandingTemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    """Service to update, get or delete a landing template(temporary)

    :accepted methods:
        PUT
        PATH
        GET
        DELETE
    """
    queryset = Template.objects.all()
    serializer_class = LandingTemplateSerializer
    permission_classes = (permissions.AllowAny,)


class TaxReceiptView(generics.ListCreateAPIView):
    """Service to create a tax receipt and attached to the signed user, get all tax receipt attached to a user

    :accepted methods:
        POST
        GET
    """
    queryset = TaxReceipt.objects.all()
    serializer_class = TaxReceiptSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        queryset = TaxReceipt.objects.filter(user=self.request.user.id)
        return queryset


class TaxReceiptDetail(generics.RetrieveUpdateDestroyAPIView):
    """Service to update, get or delete a tax receipt(temporary)

    :accepted methods:
        PUT
        PATH
        GET
        DELETE
    """
    queryset = TaxReceipt.objects.all()
    serializer_class = TaxReceiptSerializer
    permission_classes = (permissions.AllowAny,)
