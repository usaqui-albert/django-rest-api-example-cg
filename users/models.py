from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models

from countries.models import Country
from cities.models import City

class User(AbstractBaseUser):
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    country = models.OneToOneField(Country, related_name='country')
    city = models.OneToOneField(City, related_name='city')
    facebook = models.CharField(max_length=100, null=True)
    twitter = models.CharField(max_length=100, null=True)
    linked_in = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email
