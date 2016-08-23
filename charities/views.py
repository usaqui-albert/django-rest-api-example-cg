from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import SearchCharitySerializer
from benevity_library import benevity
from ConnectGood.settings import BENEVITY_API_KEY, BENEVITY_COMPANY_ID, BENEVITY_DEFAULT_PAGESIZE
from events.models import Event
from .helpers import get_charity_response, get_content_response, get_causes_response


class SearchCharity(generics.GenericAPIView):
    """

    :accepted methods:
        POST
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
            page, pagesize = self.get_pagination_params()
            response = benevity.search_causes(country=iso_code,
                                              term=serializer.validated_data['term'],
                                              page=page,
                                              pagesize=pagesize)
            if response['attrib']['status'] == 'SUCCESS':
                content = get_content_response(response['children'])
                causes = get_causes_response(content['children'])
                causes['attrib']['count'] = causes['attrib'].pop('total')
                if 'children' in causes:
                    data = dict(causes['attrib'],
                                data=get_charity_response(causes['children']))
                else:
                    data = dict(causes['attrib'], data=[])
                return Response(data, status=status.HTTP_200_OK)
            return Response('Benevity error', status=status.HTTP_409_CONFLICT)
        return Response('ConnectGood not found.', status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        obj = Event.objects.filter(
            user_event__key=self.request.data['key']).select_related('country')
        return obj

    def get_pagination_params(self):
        offset = self.request.GET.get('offset', None)
        limit = self.request.GET.get('limit', None)
        try:
            offset = int(offset) if offset else 0
            pagesize = int(limit) if limit else BENEVITY_DEFAULT_PAGESIZE
        except ValueError:
            return 1, BENEVITY_DEFAULT_PAGESIZE
        else:
            page = int(offset / pagesize) + 1
            return page, pagesize
