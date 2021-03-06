import stripe
import logging

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from stripe.error import APIConnectionError, InvalidRequestError, CardError

from rest_framework import permissions, status, views
from rest_framework.response import Response

from ConnectGood.settings import STRIPE_API_KEY
from .helpers import get_plans_list_response, filtering_plan_by_currency, reject_free_plans,\
    get_invoices_list_response, get_timestamp_from_datetime, filter_free_plans
from miscellaneous.helpers import stripe_errors_handler
from users.serializers import get_customer_in_stripe
from .serializers import UserDataSerializer
from .models import Invoice


class PlanView(views.APIView):
    """Service to get a list of Plans

    :accepted methods:
        GET
    """
    permission_classes = (permissions.AllowAny,)

    def __init__(self, **kwargs):
        super(PlanView, self).__init__(**kwargs)
        stripe.api_key = STRIPE_API_KEY
        self.logger = logging.getLogger(__name__)

    def get(self, request):
        """Method to list all plans stored in stripe handling exceptions

        :param request: To use in a future query params filtering
        :except: Api connection error from stripe
        :return: List of plans
        """
        try:
            plans = stripe.Plan.list()
        except (APIConnectionError, InvalidRequestError, CardError) as err:
            message = stripe_errors_handler(err)
            self.logger.error(message)
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        else:
            mapped_plans = get_plans_list_response(plans)
            if request.user.is_authenticated():
                customer = get_customer_in_stripe(request.user)
                if isinstance(customer, str):
                    return Response(customer, status=status.HTTP_404_NOT_FOUND)
                else:
                    currency = customer.subscriptions.data[0]['plan'].currency
                    filtered_plans = filtering_plan_by_currency(mapped_plans, str(currency))
                    no_free_plans = reject_free_plans(filtered_plans)
                    return Response(no_free_plans, status=status.HTTP_200_OK)
            country_id = request.GET.get('country', None)
            free_plans = filter_free_plans(mapped_plans)
            if country_id:
                try:
                    country_id = int(country_id)
                except ValueError:
                    pass
                else:
                    if country_id == 2:
                        currency = 'usd'
                    elif country_id == 1:
                        currency = 'cad'
                    else:
                        currency = ''
                    response = filtering_plan_by_currency(free_plans, currency)
                    return Response(response, status=status.HTTP_200_OK)
            return Response(free_plans, status=status.HTTP_200_OK)


class InvoiceView(views.APIView):
    """Service to get all the invoices of a stripe customer for the last 6 months

    :accepted methods:
        GET
    """
    permission_classes = (permissions.IsAuthenticated,)

    def __init__(self, **kwargs):
        super(InvoiceView, self).__init__(**kwargs)
        stripe.api_key = STRIPE_API_KEY
        self.logger = logging.getLogger(__name__)

    def get(self, request):
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
                message = stripe_errors_handler(err)
                self.logger.error(message)
                response = Response(message, status=status.HTTP_400_BAD_REQUEST)
            else:
                mapped_invoices = get_invoices_list_response(invoices, request.user.email)
                response = Response(mapped_invoices, status=status.HTTP_200_OK)
        return response


class InvoiceDetail(views.APIView):
    """
    :accepted methods:
        GET
    """
    permission_classes = (permissions.IsAuthenticated,)

    def __init__(self, **kwargs):
        super(InvoiceDetail, self).__init__(**kwargs)
        stripe.api_key = STRIPE_API_KEY
        self.logger = logging.getLogger(__name__)

    def get(self, request, **kwargs):
        """

        :param request:
        :return:
        """
        try:
            invoice = stripe.Invoice.retrieve(str(kwargs['invoice_id']))
        except (APIConnectionError, InvalidRequestError, CardError) as err:
            message = stripe_errors_handler(err)
            self.logger.error(message)
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        else:
            mapped_invoice = get_invoices_list_response([invoice], request.user.email)[0]
            stripe_invoice_id = str(mapped_invoice['id'])
            invoice_obj = self.get_object(stripe_invoice_id)
            if invoice_obj.exists():
                serial_number = invoice_obj.first().serial_number
            else:
                invoice_obj = Invoice.objects.create(stripe_id=stripe_invoice_id)
                invoice_obj.serial_number = serial_number = invoice_obj.generate_invoice_number()
                invoice_obj.save()
            extra_data = UserDataSerializer(request.user).data
            extra_data['invoice_number'] = serial_number
            return Response(dict(mapped_invoice, **extra_data), status=status.HTTP_200_OK)

    @staticmethod
    def get_object(stripe_id):
        return Invoice.objects.filter(stripe_id=stripe_id)
