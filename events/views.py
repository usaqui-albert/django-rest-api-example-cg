import stripe
from stripe.error import APIConnectionError, InvalidRequestError, CardError

from django.db import transaction
from django.db.models import Prefetch

from rest_framework.response import Response
from rest_framework import generics, permissions, status

from .serializers import CreateEventSerializer, EventSerializer, AcceptOrRejectEventSerializer
from .models import Event, UserEvent
from .tasks import notify_event_invitation, notify_event_accepted_user,\
    notify_event_accepted_recipient
from .helpers import validate_uuid4, get_event_status
from ConnectGood.settings import STRIPE_API_KEY, BENEVITY_API_KEY, BENEVITY_COMPANY_ID
from miscellaneous.helpers import stripe_errors_handler
from benevity_library import benevity


class EventView(generics.ListCreateAPIView):
    """Service to create a new event or get all events related with the authenticated user

    :accepted methods:
        POST
        GET
    """
    serializer_class = CreateEventSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        """Re-write of perform_create method to send the email after the event is created

        :return: Serialized event instance
        """
        user = self.request.user
        with transaction.atomic():
            event = serializer.save()
            user_event = UserEvent.objects.create(event=event, user=user)
            transaction.on_commit(
                lambda: notify_event_invitation.delay(
                    event, user, user_event.get_key_as_string()
                )
            )
        return self.serializer_class(event)

    def list(self, request, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EventSerializer(page, many=True, context={'without_sender': True})
            return self.get_paginated_response(serializer.data)

        serializer = EventSerializer(queryset, many=True, context={'without_sender': True})
        return Response(serializer.data)

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = Event.objects.filter(user_event__user=user_id).prefetch_related(
            Prefetch(
                'user_event',
                queryset=UserEvent.objects.filter(user=user_id)
            )
        )
        return queryset


class GetEventByToken(generics.RetrieveAPIView):
    """Service for a recipient to get an event detail by a unique token

    :accepted method:
        GET
    """
    serializer_class = EventSerializer
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, **kwargs):
        if validate_uuid4(kwargs['key']):
            queryset = self.get_queryset()
            if queryset.exists():
                event = queryset.first()
                self.update_event_status_as_viewed(event)
                serializer = self.serializer_class(event,
                                                   context={'host': request.get_host()})
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Event.objects.filter(user_event__key=self.kwargs['key']).prefetch_related(
            Prefetch(
                'user_event',
                queryset=UserEvent.objects.filter(key=self.kwargs['key']).select_related('user')
            )
        )
        return queryset

    def update_event_status_as_viewed(self, event):
        """Method to update the event status as viewed

        :param event: event instance
        :return: user event instance updated as viewed
        """
        user_event = event.user_event.filter(key=self.kwargs['key']).first()
        if user_event.status == user_event.WAITING:
            user_event.status = user_event.VIEWED
            user_event.save()
        return user_event


class AcceptOrRejectEvent(generics.GenericAPIView):
    """Service to handle when a recipient accept or reject a CG invitation

    :accepted methods:
        POST
    """
    def __init__(self, *args, **kwargs):
        super(AcceptOrRejectEvent, self).__init__(*args, **kwargs)
        stripe.api_key = STRIPE_API_KEY
        benevity.api_key = BENEVITY_API_KEY
        benevity.company_id = BENEVITY_COMPANY_ID

    permission_classes = (permissions.AllowAny,)
    serializer_class = AcceptOrRejectEventSerializer

    def post(self, request):
        """

        :param request:
        :return:
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_event = self.get_object()
        if user_event.exists():
            event_status = get_event_status(serializer.validated_data['status'])
            response = self.handle_accept_or_reject(user_event.first(),
                                                    event_status,
                                                    serializer.validated_data['charity'])
            if response is True:
                user_event = self.get_object()
                return_serializer = EventSerializer(user_event.first().event)
                return Response(return_serializer.data, status=status.HTTP_200_OK)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def handle_accept_or_reject(self, user_event, event_status, charity):
        """Method to handle when a user reject or accept a CG invitation

        :param user_event: user_event instance
        :param event_status: status of the event, example: 'ACCEPTED'
        :return:
        """
        event = user_event.event
        user = user_event.user
        if event_status == user_event.REJECTED:
            user_event.status = user_event.REJECTED
            response = True
        else:
            country = event.country
            user_event.status = user_event.ACCEPTED
            try:
                stripe.Charge.create(
                    amount=int(event.donation_amount * 100),
                    currency=country.currency,
                    customer=user.user_customer.first().customer_id,
                    description="Charge for " + user.__str__()
                )
            except (APIConnectionError, InvalidRequestError, CardError) as err:
                return stripe_errors_handler(err)
            else:
                response = self.benevity_process(user, event, charity)
        user_event.save()
        return response

    @staticmethod
    def benevity_process(user, event, charity):
        if not user.added_to_benevity:
            # Adding a new user to benevity
            response = benevity.add_user(**get_user_params(user))
            if response['attrib']['status'] == 'FAILED':
                return 'There was an error adding a user in benevity'
            user.added_to_benevity = True
            user.save()

        credits_to_transfer = str(int(event.donation_amount * 100))
        refno = 'CG%s' % str(event.id)
        user_benevity_id = str(user.benevity_id)

        # ConnectGood transfers credits to the user
        transference = benevity.company_transfer_credits_to_user(
            cashable='no',
            user=user_benevity_id,
            credits=credits_to_transfer,
            refno=refno
        )
        if transference['attrib']['status'] == 'FAILED':
            return 'There was an error transferring credits to the user'
        # User transfers credits to a cause(charity)
        transfer = benevity.user_transfer_credits_to_causes(
            user=str(user.benevity_id),
            credits=credits_to_transfer,
            refno=refno,
            cause=charity
        )
        if transfer['attrib']['status'] == 'FAILED':
            return 'There was an error transferring credits to a charity'
        # Generating the receipt of the day for this user
        receipt = benevity.generate_user_receipts(user=user_benevity_id,
                                                  start='2016-08-31')
        if receipt['attrib']['status'] == 'FAILED':
            return 'There was an error generating the receipt for this user'
        event.receipt_id = 'D6399685NT'
        event.save()
        notify_event_accepted_user.delay(event, user)
        notify_event_accepted_recipient.delay(event, user)
        return True

    def get_object(self):
        obj = UserEvent.objects.filter(key=self.request.data['key']).select_related(
            'event__country', 'user__country')
        return obj

def get_user_params(user):
    """

    :param user: user object
    :return: dictionary with the necessary fields to do the benevity request
    """
    return {
        'email': str(user.email),
        'firstname': str(user.first_name),
        'lastname': str(user.last_name),
        'active': 'yes',
        'user': str(user.benevity_id),
        'address-city': str(user.city),
        'address-country': str(user.get_country_iso_code()),
        'address-postcode': str(user.zip_code),
        'address-state': str(user.get_state_as_string()),
        'address-street': str(user.street_address)
    }
