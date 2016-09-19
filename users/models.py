import uuid

from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models

from countries.models import Country
from states.models import State

CONDITION_CHOICES = ((1, 'User'), (2, 'Company'))


class User(AbstractBaseUser):
    """Model for User object"""
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, null=True)
    street_address = models.TextField()
    country = models.ForeignKey(Country, related_name='country')
    city = models.CharField(max_length=100)
    province = models.ForeignKey(State, related_name='state')
    phone_number = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)

    tax_receipts_as = models.IntegerField(choices=CONDITION_CHOICES)

    added_to_benevity = models.BooleanField(default=False)
    benevity_id = models.UUIDField(default=uuid.uuid4, editable=False)

    has_a_plan = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_tax_receipts_as_string(self):
        """Method to get the tax receipts value as a description"""
        return self.get_full_name() if self.tax_receipts_as == 1 else self.company

    def get_full_name(self):
        return str(self.first_name + " " + self.last_name)

    def is_corporate_account(self):
        """Method to get a boolean indicating if this object is a corporate account or not"""
        return self.tax_receipts_as == 2

    def get_country_iso_code(self):
        """Method to get the country iso code of this user"""
        return self.country.iso_code

    def get_state_as_string(self):
        """Method to get the province/state value of this user as string"""
        return self.province.__str__()
