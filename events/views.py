from django.db import transaction
from rest_framework import generics, permissions
from django.contrib.auth.tokens import default_token_generator

from .serializers import *
from .models import *
from .tasks import send_email_to_notify
from events.models import UserEvent


class EventView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
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
