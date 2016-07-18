import datetime
import uuid

from django.db import models
from django.utils import timezone

from countries.models import Country
from miscellaneous.models import TaxReceipt
from users.models import User


class Event(models.Model):
    """Model of the event object"""
    recipient_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    country = models.ForeignKey(Country, related_name='event_country')
    landing_message = models.TextField()
    donation_amount = models.DecimalField(max_digits=7, decimal_places=2)
    card_id = models.CharField(max_length=100)
    tax_receipt = models.ForeignKey(TaxReceipt, related_name='tax_receipt', null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Event ' + str(self.id)


class UserEvent(models.Model):
    """Pivot table to set the relation between User and Events tables"""
    user = models.ForeignKey(User, related_name='user_event')
    event = models.ForeignKey(Event, related_name='user_event')
    key = models.UUIDField(default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_key_expired(self):
        return self.created_at <= timezone.now() - datetime.timedelta(days=15)
