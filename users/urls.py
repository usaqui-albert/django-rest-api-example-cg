"""User URL Configuration"""

from django.conf.urls import url
from .views import UserView, UserDetail

urlpatterns = [
    url(r'^$', UserView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', UserDetail.as_view())

]
