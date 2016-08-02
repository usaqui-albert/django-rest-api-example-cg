import stripe
from stripe.error import APIConnectionError, InvalidRequestError, CardError

from django.db import transaction
from django.db.models import Prefetch

from rest_framework.response import Response
from rest_framework import generics, permissions, status

from .serializers import CreateEventSerializer, EventSerializer, AcceptOrRejectEventSerializer
from .models import Event, UserEvent
from .tasks import send_email_to_notify
from .helpers import validate_uuid4, get_event_status, update_event_status
from ConnectGood.settings import STRIPE_API_KEY


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
                lambda: send_email_to_notify.delay(event, user, user_event.get_key_as_string())
            )
        return self.serializer_class(event)

    def list(self, request, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Event.objects.filter(user_event__user=self.request.user.id)
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
                serializer = self.serializer_class(queryset.get(), context={'host': request.get_host()})
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = Event.objects.filter(user_event__key=self.kwargs['key']).prefetch_related(
            Prefetch('user_event', queryset=UserEvent.objects.filter(key=self.kwargs['key'])))
        return queryset


class AcceptOrRejectEvent(generics.GenericAPIView):
    """

    :accepted methods:
        POST
    """
    def __init__(self, *args, **kwargs):
        super(AcceptOrRejectEvent, self).__init__(*args, **kwargs)
        stripe.api_key = STRIPE_API_KEY

    permission_classes = (permissions.AllowAny,)
    serializer_class = AcceptOrRejectEventSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_event = UserEvent.objects.filter(key=serializer.validated_data['key']).\
            select_related('event__country', 'user')
        if user_event.exists():
            event_status = get_event_status(serializer.validated_data['status'])
            response = self.handle_accept_or_reject(user_event.get(), event_status)
            if isinstance(response, str):
                response = Response({'stripe_error': [response]}, status=status.HTTP_400_BAD_REQUEST)
            elif response:
                response = Response(serializer.data, status=status.HTTP_200_OK)
            else:
                response = Response({"database_error": ['There was a conflict updating the database']},
                                    status=status.HTTP_409_CONFLICT)
            return response
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def handle_accept_or_reject(user_event, event_status):
        if event_status == user_event.REJECTED:
            pass  # TODO: send an email to the sender notifying that the connect good was rejected
        elif event_status == user_event.ACCEPTED:
            event = user_event.event
            country = event.country
            user = user_event.user
            try:
                stripe.Charge.create(
                    amount=int(event.donation_amount * 100),
                    currency=country.currency,
                    customer=user.user_customer.get(),
                    description="Charge for " + user.__str__()
                )
            except (APIConnectionError, InvalidRequestError, CardError) as e:
                response = ''
                if isinstance(e, APIConnectionError):
                    response = str(e).split('.')[0]
                if isinstance(e, InvalidRequestError) or isinstance(e, CardError):
                    body = e.json_body
                    response = str(body['error']['message'])
                return response
            else:
                pass  # TODO: send an email to the sender notifying that the connect good was accepted
        return update_event_status(user_event, event_status)
