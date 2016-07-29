from rest_framework import generics, permissions
from .serializers import CharityCountrySerializer
from .models import CharityCountry


class CharityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CharityCountry.objects.all()
    serializer_class = CharityCountrySerializer
    permission_classes = (permissions.AllowAny,)
