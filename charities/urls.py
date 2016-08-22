"""Charities URL Configuration"""

from django.conf.urls import url
from .views import CharityDetail, SearchCharity

urlpatterns = [
    url(r'^$', SearchCharity.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', CharityDetail.as_view())

]
