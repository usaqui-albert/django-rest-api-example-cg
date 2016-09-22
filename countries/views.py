from rest_framework import generics, permissions

from .serializers import CountrySerializer
from .models import Country
from states.models import State
from states.serializers import StateSerializer


class CountryView(generics.ListCreateAPIView):
    """Service to create a new country or list all countries(temporary)

    :accepted methods:
        POST
        GET
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class StatesList(generics.ListAPIView):
    """

    :accepted methods:
        GET
    """
    serializer_class = StateSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = State.objects.filter(country=self.kwargs['pk'])
        return queryset
