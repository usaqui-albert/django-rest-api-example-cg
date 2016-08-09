import datetime

from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone

from countries.models import Country
from states.models import State

CONDITION_CHOICES = ((1, 'User'), (2, 'Company'))


class User(AbstractBaseUser):
    """Model for User object"""
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    street_address = models.TextField()
    country = models.ForeignKey(Country, related_name='country')
    city = models.CharField(max_length=100)
    province = models.ForeignKey(State, related_name='state')
    facebook = models.CharField(max_length=100, null=True)
    twitter = models.CharField(max_length=100, null=True)
    linkedin = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    free_trial_started_at = models.DateTimeField(null=True)
    has_a_plan = models.BooleanField(default=False)
    tax_receipts_as = models.IntegerField(choices=CONDITION_CHOICES)
    zip_code = models.CharField(max_length=10)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email

    def free_trial_is_over(self):
        """Method to check if a free trial from a user has finished

        :return: True if the free trial has finished, otherwise False
        """
        if self.free_trial_started_at:
            return self.free_trial_started_at <= timezone.now() - datetime.timedelta(days=15)

    def free_trial_has_started(self):
        """Method to check if a free trial from a user has already started

        :return: True if the free trial has already started, otherwise False
        """
        return self.free_trial_started_at is not None

    def start_free_trial(self):
        """Method to set the free_trial_started_at user field to date object(now)

        :return: True
        """
        self.free_trial_started_at = timezone.now()
        return True

    def get_tax_receipts_as_string(self):
        return self.get_full_name() if self.tax_receipts_as == 1 else self.company

    def get_full_name(self):
        return self.first_name + " " + self.last_name
