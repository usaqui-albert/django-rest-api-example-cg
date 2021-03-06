from django.db import models
from users.models import User


class CustomerStripe(models.Model):
    """Model to store the customer id of Stripe"""
    customer_id = models.CharField(max_length=100)
    user = models.ForeignKey(User, related_name='user_customer')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
