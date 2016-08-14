import stripe
from stripe.error import APIConnectionError, InvalidRequestError, CardError

from django.db import transaction
from django.db.models import Prefetch

from rest_framework.response import Response
from rest_framework import generics, permissions, status

from .serializers import CreateEventSerializer, EventSerializer, AcceptOrRejectEventSerializer
from .models import Event, UserEvent
from .tasks import notify_event_invitation, notify_event_accepted, notify_event_rejected
from .helpers import validate_uuid4, get_event_status, update_event_status
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
            serializer = EventSerializer(page, many=True, context={'no_sender': True})
            return self.get_paginated_response(serializer.data)

        serializer = EventSerializer(queryset, many=True, context={'no_sender': True})
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
        user_event = UserEvent.objects.filter(key=serializer.validated_data['key']).\
            select_related('event__country', 'user')
        if user_event.exists():
            event_status = get_event_status(serializer.validated_data['status'])
            response = self.handle_accept_or_reject(user_event.first(), event_status)
            if isinstance(response, str):
                response = Response(response, status=status.HTTP_400_BAD_REQUEST)
            elif response:
                response = Response(serializer.data, status=status.HTTP_200_OK)
            else:
                database_error = 'There was a conflict updating the database'
                response = Response(database_error, status=status.HTTP_409_CONFLICT)
            return response
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def handle_accept_or_reject(user_event, event_status):
        """Method to handle when a user reject or accept a CG invitation

        :param user_event: user_event instance
        :param event_status: status of the event, example: 'ACCEPTED'
        :return:
        """
        event = user_event.event
        user = user_event.user
        if event_status == user_event.REJECTED:
            notify_event_rejected.delay(event, user)
        else:
            country = event.country
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
                if not user.added_to_benevity:
                    response = benevity.add_user(**get_user_params(user))
                    if isinstance(response, str):
                        return response
                    # TODO: set the added_to_benevity attribute of user as True
                transfer_params = {
                    'cashable': 'no',
                    'user': str(user.benevity_id),
                    'credits': str(int(event.donation_amount * 100)),
                    'refno': 'CG%s' % str(event.id)
                }
                res = benevity.company_transfer_credits_to_user(**transfer_params)
                if isinstance(res, str):
                    return res
                notify_event_accepted.delay(event, user)
        return update_event_status(user_event, event_status)

def get_user_params(user):
    """

    :param user: user object
    :return: dictionary with the necessary fields to do the benevity request
    """
    return {
        'email': user.email,
        'firstname': user.first_name,
        'lastname': user.last_name,
        'active': 'yes',
        'user': str(user.benevity_id)
    }
