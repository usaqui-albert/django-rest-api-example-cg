from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import *
from .models import *


class CountryView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (permissions.AllowAny,)
