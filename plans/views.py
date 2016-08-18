import stripe
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from stripe.error import APIConnectionError, InvalidRequestError, CardError

from rest_framework import permissions, status, views
from rest_framework.response import Response

from ConnectGood.settings import STRIPE_API_KEY
from .helpers import get_response_plan_list, filtering_plan_by_currency, reject_free_plans,\
    get_response_invoice_list, get_timestamp_from_datetime
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
                if isinstance(customer, str):
                    response = Response(customer, status=status.HTTP_404_NOT_FOUND)
                else:
                    currency = customer.subscriptions.data[0]['plan'].currency
                    filtered_plans = filtering_plan_by_currency(mapped_plans, str(currency))
                    no_free_plans = reject_free_plans(filtered_plans)
                    response = Response(no_free_plans, status=status.HTTP_200_OK)
            else:
                response = Response(mapped_plans, status=status.HTTP_200_OK)
        return response


class InvoiceView(views.APIView):
    """Service to get all the invoices of a stripe customer for the last 6 months

    :accepted methods:
        GET
    """
    permission_classes = (permissions.IsAuthenticated,)

    def __init__(self, **kwargs):
        super(InvoiceView, self).__init__(**kwargs)
        stripe.api_key = STRIPE_API_KEY

    @staticmethod
    def get(request):
        """Method to get the invoices of a user(customer) from stripe

        :param request: user requesting instance
        :return:  Http 200 if the getting data was success
        :except: Http 404 if the user doesn't have a customer in stripe, Http 400 if the request
        to the stripe api returns an error
        """
        customer = get_customer_in_stripe(request.user)
        if isinstance(customer, str):
            response = Response(customer, status=status.HTTP_404_NOT_FOUND)
        else:
            unix_timestamp = get_timestamp_from_datetime(timezone.now() - relativedelta(months=+6))
            try:
                invoices = stripe.Invoice.list(customer=customer.id, date={'gte': unix_timestamp})
            except (APIConnectionError, InvalidRequestError, CardError) as err:
                response = Response(stripe_errors_handler(err), status=status.HTTP_400_BAD_REQUEST)
            else:
                mapped_invoices = get_response_invoice_list(invoices)
                response = Response(mapped_invoices, status=status.HTTP_200_OK)
        return response
