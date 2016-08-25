"""ConnectGood URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include

from users.views import LoginView
from plans.views import PlanView
from ConnectGood.settings import MEDIA_ROOT

urlpatterns = [
    url(r'^api/v1/login/', LoginView.as_view()),
    url(r'^api/v1/plans/$', PlanView.as_view()),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
    url(r'^docs/', include('rest_framework_docs.urls')),

    url(r'^api/v1/users/', include('users.urls')),
    url(r'^api/v1/countries/', include('countries.urls')),
    url(r'^api/v1/events/', include('events.urls')),
    url(r'^api/v1/invoices/', include('plans.urls')),
    url(r'^api/v1/charities/', include('charities.urls'))
]
