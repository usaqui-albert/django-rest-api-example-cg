from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import CharityCountrySerializer, SearchCharitySerializer
from .models import CharityCountry
from benevity_library import benevity
from ConnectGood.settings import BENEVITY_API_KEY, BENEVITY_COMPANY_ID
from events.models import Event
from .helpers import get_charity_response, get_content_response, get_causes_response


class CharityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = CharityCountry.objects.all()
    serializer_class = CharityCountrySerializer
    permission_classes = (permissions.AllowAny,)


class SearchCharity(generics.GenericAPIView):
    """
    :accepted methods:

    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = SearchCharitySerializer

    def __init__(self, **kwargs):
        super(SearchCharity, self).__init__(**kwargs)
        benevity.api_key = BENEVITY_API_KEY
        benevity.company_id = BENEVITY_COMPANY_ID

    def post(self, request):
        """

        :param request:
        :return:
        """
        serializer = SearchCharitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = self.get_queryset()
        if event.exists():
            iso_code = event.first().country.iso_code
            response = benevity.search_causes(country=iso_code,
                                              term=serializer.validated_data['term'])
            if response['attrib']['status'] == 'SUCCESS':
                content = get_content_response(response['children'])
                causes = get_causes_response(content['children'])
                # data = dict(causes['attrib'], data=get_charity_response(content['children']))
                return Response(causes, status=status.HTTP_200_OK)
            return Response('Benevity error', status=status.HTTP_409_CONFLICT)
        return Response('ConnectGood not found.', status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        obj = Event.objects.filter(user_event__key=self.request.data['key']).select_related('country')
        return obj
