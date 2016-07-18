from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', EventView.as_view()),
    url(r'^key/(?P<key>[0-9A-Za-z-]+)/$', GetEventByToken.as_view()),
]
