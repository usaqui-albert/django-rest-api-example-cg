from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ConnectGood.settings import BENEVITY_API_KEY, BENEVITY_COMPANY_ID
from benevity_library import benevity


class BenevityReceiptView(generics.GenericAPIView):
    """

    :accepted methods:
        GET
    """
    def __init__(self, *args, **kwargs):
        super(BenevityReceiptView, self).__init__(*args, **kwargs)
        benevity.api_key = BENEVITY_API_KEY
        benevity.company_id = BENEVITY_COMPANY_ID

    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def get(request):
        """

        :param request:
        :return:
        """
        pass
