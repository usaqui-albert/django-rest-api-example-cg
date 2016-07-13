import datetime

from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone

from countries.models import Country
from cities.models import City

class User(AbstractBaseUser):
    """Model for User object"""
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    street_address = models.TextField()
    country = models.OneToOneField(Country, related_name='country')
    city = models.OneToOneField(City, related_name='city')
    facebook = models.CharField(max_length=100, null=True)
    twitter = models.CharField(max_length=100, null=True)
    linkedin = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    free_trial_started_at = models.DateTimeField(null=True)
    has_a_plan = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email

    def free_trial_is_over(self):
        if self.free_trial_started_at:
            return self.free_trial_started_at <= timezone.now() - datetime.timedelta(days=15)

    def free_trial_has_started(self):
        return self.free_trial_started_at is not None
