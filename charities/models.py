from django.db import models
from countries.models import Country


class CharityCategory(models.Model):
    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CharityCountry(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, related_name='country_charity')
    charity = models.ForeignKey(CharityCategory, related_name='country_charity')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
