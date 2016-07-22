from django.db import models


class PromoCode(models.Model):
    """Model for the promo codes"""
    code = models.CharField(max_length=100, unique=True)
    used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
