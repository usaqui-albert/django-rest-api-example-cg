"""Charities URL Configuration"""

from django.conf.urls import url
from .views import SearchCharity

urlpatterns = [
    url(r'^$', SearchCharity.as_view())

]
