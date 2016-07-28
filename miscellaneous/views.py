import stripe

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from .models import CustomerStripe
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

    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def post(request):
        """User adds a new credit card to his related customer in stripe

        :param request: data (JSON requested) and user (User instance)
        :raise: Http 404 if the user does not have customer related in stripe
        :return: Http 201 if the card was added to the customer successfully
        """
        customer_stripe = get_object_or_404(CustomerStripe, user=request.user.id)
        customer = stripe.Customer.retrieve(customer_stripe.customer_id)
        customer.sources.create(source=request.data["card_token"])
        return Response(status=status.HTTP_201_CREATED)

    @staticmethod
    def get(request):
        """User gets a credit cards list information

        :param request: user (User instance)
        :raise: Http 404 if the user does not have customer related in stripe
        :return: Http 200 with a list of his credit cards information
        """
        customer_stripe = get_object_or_404(CustomerStripe, user=request.user.id)
        customer = stripe.Customer.retrieve(customer_stripe.customer_id)
        cards_response = customer.sources.all(limit=3, object='card')
        return Response(card_list(cards_response.data))
