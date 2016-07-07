from django.db import models


class PaymentMethod(models.Model):
    """Model of the PaymentMethod Object"""
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Template(models.Model):
    """Model of the templates to use in the style of the landing pages"""
    name = models.CharField(max_length=100)
    css = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TaxReceipt(models.Model):
    """Model of the tax receipt"""
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
