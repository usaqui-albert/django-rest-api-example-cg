from django.db import transaction
from django.contrib.auth.tokens import default_token_generator

from rest_framework.response import Response
from rest_framework import generics, permissions, status

from .serializers import *
from .models import *
from .tasks import send_email_to_notify
from events.models import UserEvent


class EventView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = CreateEventSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        """Re-write of perform_create method to send the email after the event is created

        :return: Serialized event instance
        """
        user = self.request.user
        with transaction.atomic():
            event = serializer.save()
            key = default_token_generator.make_token(user)
            UserEvent.objects.create(event=event, user=user, key=key)
            transaction.on_commit(lambda: send_email_to_notify.delay(event, user, key))
        return self.serializer_class(event)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Event.objects.filter(user_event__user=self.request.user.id)
        return queryset


class GetEventByToken(generics.RetrieveAPIView):
    serializer_class = EventSerializer
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Event.objects.filter(user_event__key=self.kwargs['key'])
        return queryset
