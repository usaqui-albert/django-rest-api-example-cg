from django.conf.urls import url
from .views import CountryView

urlpatterns = [
    url(r'^$', CountryView.as_view()),
]
