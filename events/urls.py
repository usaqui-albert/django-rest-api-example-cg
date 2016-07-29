from django.conf.urls import url
from .views import EventView, GetEventByToken, AcceptOrRejectEvent

urlpatterns = [
    url(r'^$', EventView.as_view()),
    url(r'^key/(?P<key>[0-9A-Za-z-]+)/$', GetEventByToken.as_view()),
    url(r'^status/$', AcceptOrRejectEvent.as_view())
]
