import datetime

from django.test import TestCase
from django.utils import timezone

from .models import User
from countries.models import Country
from states.models import State

class UserTestCase(TestCase):
    """Test cases for methods of the User Object"""
    user = {
        'id': 1,
        'email': '',
        'password': '12345678',
        'first_name': 'John',
        'last_name': 'Doe',
        'street_address': 'Test street address',
        'company': 'Test company name',
        'phone_number': '123-4567',
        'tax_receipts_as': 1,
        'zip_code': '123-456',
        'city': 'Caracas'
    }
    country = {
        'name': 'Venezuela'
    }
    province = {
        'name': 'Dto. Capital'
    }

    def setUp(self):
        country = Country.objects.create(**self.country)
        self.province['country'] = self.user['country'] = country
        self.user['province'] = State.objects.create(**self.province)
        User.objects.create(**self.user)

    def test_free_trial_is_over_one_day_left(self):
        user = User.objects.get(id=1)
        user.free_trial_started_at = timezone.now() - datetime.timedelta(days=14)
        self.assertFalse(user.free_trial_is_over())

    def test_free_trial_is_over_one_day_past(self):
        user = User.objects.get(id=1)
        user.free_trial_started_at = timezone.now() - datetime.timedelta(days=16)
        self.assertTrue(user.free_trial_is_over())

    def test_free_trial_is_over_border_case_day(self):
        """The border case day is 15th, this case should return True"""
        user = User.objects.get(id=1)
        user.free_trial_started_at = timezone.now() - datetime.timedelta(days=15)
        self.assertTrue(user.free_trial_is_over())

    def test_free_trial_is_over_one_second_left(self):
        __datetime__ = {
            'days': 14,
            'hours': 23,
            'minutes': 59,
            'seconds': 59
        }
        user = User.objects.get(id=1)
        user.free_trial_started_at = timezone.now() - datetime.timedelta(**__datetime__)
        self.assertFalse(user.free_trial_is_over())

    def test_free_trial_is_over_one_second_past(self):
        __datetime__ = {
            'days': 15,
            'hours': 0,
            'minutes': 0,
            'seconds': 1
        }
        user = User.objects.get(id=1)
        user.free_trial_started_at = timezone.now() - datetime.timedelta(**__datetime__)
        self.assertTrue(user.free_trial_is_over())

    def test_free_trial_has_started_not_started(self):
        """When a user has not started free trial this method should return False"""
        user = User.objects.get(id=1)
        user.free_trial_started_at = None
        self.assertFalse(user.free_trial_has_started())

    def test_free_trial_has_started_already_started(self):
        """When a user has started free trial this method should return True"""
        user = User.objects.get(id=1)
        user.free_trial_started_at = timezone.now()
        self.assertTrue(user.free_trial_has_started())

    def test_free_trial_has_started_and_over(self):
        """When a user started free trial and over it this method should return True"""
        user = User.objects.get(id=1)
        user.free_trial_started_at = timezone.now() - datetime.timedelta(days=16)
        self.assertTrue(user.free_trial_has_started())
