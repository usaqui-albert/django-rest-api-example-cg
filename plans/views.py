import stripe
from stripe.error import APIConnectionError, InvalidRequestError, CardError

from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from ConnectGood.settings import STRIPE_API_KEY
from miscellaneous.models import CustomerStripe
from .serializers import SubscriptionSerializer
from .helpers import get_response_plan_list, filtering_plan_by_currency, reject_free_plans
from miscellaneous.helpers import stripe_errors_handler
from users.serializers import get_customer_in_stripe


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
        except (APIConnectionError, InvalidRequestError, CardError) as err:
            return Response(stripe_errors_handler(err), status=status.HTTP_400_BAD_REQUEST)
        else:
            mapped_plans = get_response_plan_list(plans)
            if request.user.is_authenticated():
                customer = get_customer_in_stripe(request.user)
                currency = customer.subscriptions.data[0]['plan'].currency
                filtered_plans = filtering_plan_by_currency(mapped_plans, str(currency))
                no_free_plans = reject_free_plans(filtered_plans)
                response = Response(no_free_plans, status=status.HTTP_200_OK)
            else:
                response = Response(mapped_plans, status=status.HTTP_200_OK)
        return response


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
        except (APIConnectionError, InvalidRequestError, CardError) as err:
            return Response(stripe_errors_handler(err), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_201_CREATED)
