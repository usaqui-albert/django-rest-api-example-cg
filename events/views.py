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
                lambda: send_email_to_notify.delay(event, user, user_event.get_key_as_string())
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
                serializer = self.serializer_class(queryset.first(),
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
                response = Response({'stripe_error': [response]},
                                    status=status.HTTP_400_BAD_REQUEST)
            elif response:
                response = Response(serializer.data, status=status.HTTP_200_OK)
            else:
                database_error = 'There was a conflict updating the database'
                response = Response({'database_error': [database_error]},
                                    status=status.HTTP_409_CONFLICT)
            return response
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def handle_accept_or_reject(user_event, event_status):
        """

        :param user_event:
        :param event_status:
        :return:
        """
        if event_status == user_event.REJECTED:
            pass  # TODO: send an email to the sender that the connect good was rejected
        elif event_status == user_event.ACCEPTED:
            event = user_event.event
            country = event.country
            user = user_event.user
            try:
                stripe.Charge.create(
                    amount=int(event.donation_amount * 100),
                    currency=country.currency,
                    customer=user.user_customer.first().customer_id,
                    description="Charge for " + user.__str__()
                )
            except (APIConnectionError, InvalidRequestError, CardError) as err:
                return Response(stripe_errors_handler(err), status=status.HTTP_400_BAD_REQUEST)
            else:
                if not user.added_to_benevity:
                    response = benevity.add_user(**get_user_params(user))
                    if isinstance(response, str):
                        return Response(response, status=status.HTTP_409_CONFLICT)
                transfer_params = {
                    'cashable': 'no',
                    'user': str(user.benevity_id),
                    'credits': str(int(event.donation_amount * 100)),
                    'refno': 'CG%s' % str(event.id)
                }
                res = benevity.company_transfer_credits_to_user(**transfer_params)
                if isinstance(res, str):
                    return Response({'benevity_error': [res]}, status=status.HTTP_409_CONFLICT)
                # TODO: send an email to the sender that the connect good was accepted
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
