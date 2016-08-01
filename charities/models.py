from django.db import models
from countries.models import Country
from .helpers import PathAndRename


class CharityCategory(models.Model):
    """Model for the categories of charities"""
    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CharityCountry(models.Model):
    """Model for the charities, pivot table between charity category and country"""
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, related_name='country_charity')
    charity = models.ForeignKey(CharityCategory, related_name='country_charity')
    picture = models.ImageField(upload_to=PathAndRename('charities'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_path_picture(self):
        return str(self.picture)
