from rest_framework import generics, permissions

from .serializers import CountrySerializer
from .models import Country


class CountryView(generics.ListCreateAPIView):
    """Service to create a new country or list all countries(temporary)

    :accepted methods:
        POST
        GET
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (permissions.AllowAny,)
