from rest_framework import generics, permissions
from django.db.models import Prefetch

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


class CountryDetail(generics.RetrieveAPIView):
    """Service to get the detail(states) from an specific country

    :accepted methods:
        GET
    """
    serializer_class = CountrySerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        queryset = Country.objects.filter(id=self.kwargs['pk']).prefetch_related(
            Prefetch('states', queryset=State.objects.filter(country=self.kwargs['pk'])))
        return queryset


class StatesList(generics.ListAPIView):
    """

    :accepted methods:
        GET
    """
    serializer_class = StateSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        queryset = State.objects.filter(country=self.kwargs['pk'])
        return queryset
