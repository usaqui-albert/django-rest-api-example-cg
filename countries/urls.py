from django.conf.urls import url
from .views import CountryView, CountryDetail, StatesList

urlpatterns = [
    url(r'^$', CountryView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', CountryDetail.as_view()),
    url(r'^(?P<pk>[0-9]+)/states/$', StatesList.as_view())
]
