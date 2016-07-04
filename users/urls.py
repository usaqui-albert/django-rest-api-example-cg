from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', UserView.as_view()),

]
