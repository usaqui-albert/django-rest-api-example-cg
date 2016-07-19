from django.db import transaction

from rest_framework.response import Response
from rest_framework import generics, permissions

from .serializers import CreateEventSerializer, EventSerializer
from .models import Event, UserEvent
from .tasks import send_email_to_notify


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
            transaction.on_commit(lambda: send_email_to_notify.delay(event, user, user_event.key))
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
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Event.objects.filter(user_event__key=self.kwargs['key'])
        return queryset
