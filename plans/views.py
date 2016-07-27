import stripe

from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from ConnectGood.settings import STRIPE_API_KEY
from .models import PromoCode
from miscellaneous.models import CustomerStripe
from .serializers import SubscriptionSerializer, PromoCodeSerializer, CheckCodeSerializer
from .helpers import get_response_plan_list


class PlanView(views.APIView):
    """Service to get a list of Plans

    :accepted methods:
        GET
    """
    permission_classes = (permissions.AllowAny,)

    def __init__(self, **kwargs):
        super(PlanView, self).__init__(**kwargs)
        stripe.api_key = STRIPE_API_KEY

    @staticmethod
    def get(request):
        """Method to list all plans stored in stripe handling exceptions

        :param request: To use in a future query params filtering
        :except: Api connection error from stripe
        :return: List of plans
        """
        try:
            plans = stripe.Plan.list()
        except stripe.error.APIConnectionError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(get_response_plan_list(plans), status=status.HTTP_200_OK)


class SubscriptionView(generics.GenericAPIView):
    """Method to subscribe to a plan a user(customer) in stripe

    :accepted methods:
        POST
    """
    def __init__(self, **kwargs):
        super(SubscriptionView, self).__init__(**kwargs)
        stripe.api_key = STRIPE_API_KEY

    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        """

        :param request: data (JSON request)
        :except: Invalid request error from stripe
        :return: Http 201 if the subscription is successfully
        """
        customer_stripe = get_object_or_404(CustomerStripe, user=request.user.id)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            stripe.Subscription.create(
                customer=customer_stripe.customer_id,
                plan=serializer.validated_data['plan_id']
            )
        except stripe.error.InvalidRequestError as e:
            body = e.json_body
            return Response(body, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_201_CREATED)


class PromoCodeView(generics.CreateAPIView):
    """Service for an admin to create a new promo code

    :accepted methods:
        POST
    """
    serializer_class = PromoCodeSerializer
    permission_classes = (permissions.IsAdminUser,)


class CheckingPromoCode(views.APIView):
    """Service to check if a promo code is valid or not

    :accepted methods:
        POST
    """
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request):
        """

        :param request:
        :return:
        """
        serializer = CheckCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        promo_code = get_object_or_404(PromoCode, code=serializer.validated_data['promo_code'])
        if promo_code.used:
            return Response({'promo_code': ['Promo code already used']}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({'promo_code': ['Valid Promo code']}, status=status.HTTP_200_OK)
