from django.db import transaction
from django.db.models import Prefetch

from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.generics import get_object_or_404

from .serializers import CreateEventSerializer, EventSerializer, AcceptOrRejectEventSerializer
from .models import Event, UserEvent
from .tasks import send_email_to_notify
from .helpers import validate_uuid4, get_event_status


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
    permission_classes = (permissions.AllowAny,)
    serializer_class = AcceptOrRejectEventSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_event = get_object_or_404(UserEvent, key=serializer.validated_data['key'])
        event_status = get_event_status(serializer.validated_data['status'])
        if event_status == user_event.REJECTED:
            user_event.status = event_status
            user_event.save()
        elif event_status == user_event.ACCEPTED:
            user_event.status = user_event.ACCEPTED
            user_event.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
