import datetime
import uuid

from django.db import models
from django.utils import timezone

from countries.models import Country
from users.models import User


class Event(models.Model):
    """Model of the event object"""
    recipient_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100)
    country = models.ForeignKey(Country, related_name='event_country')
    landing_message = models.TextField()
    donation_amount = models.DecimalField(max_digits=7, decimal_places=2)
    card_id = models.CharField(max_length=100)
    receipt_id = models.CharField(max_length=100, null=True)
    refno_benevity = models.UUIDField(default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserEvent(models.Model):
    """Pivot table to set the relation between User and Events tables"""
    ACCEPTED = 'A'
    REJECTED = 'R'
    WAITING = 'W'
    VIEWED = 'V'
    BOUNCED = 'B'
    EXPIRED = 'E'
    STATUS_OF_THE_EVENT = (
        (ACCEPTED, 'ACCEPTED'),
        (REJECTED, 'REJECTED'),
        (WAITING, 'WAITING'),
        (VIEWED, 'VIEWED'),
        (BOUNCED, 'BOUNCED'),
        (EXPIRED, 'EXPIRED')
    )

    user = models.ForeignKey(User, related_name='user_event')
    event = models.ForeignKey(Event, related_name='user_event')
    key = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=1, choices=STATUS_OF_THE_EVENT, default=WAITING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_key_expired(self):
        return self.created_at <= timezone.now() - datetime.timedelta(days=30)

    def get_status_as_string(self):
        return [y for x, y in self.STATUS_OF_THE_EVENT if x == self.status][0]

    def get_key_as_string(self):
        return str(self.key).replace('-', '')
