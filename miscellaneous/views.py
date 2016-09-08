import base64

from rest_framework import permissions, views, status
from rest_framework.response import Response

from ConnectGood.settings import BENEVITY_API_KEY, BENEVITY_COMPANY_ID
from benevity_library import benevity
from events.models import Event


class BenevityReceiptView(views.APIView):
    """

    :accepted methods:
        GET
    """
    def __init__(self, *args, **kwargs):
        super(BenevityReceiptView, self).__init__(*args, **kwargs)
        benevity.api_key = BENEVITY_API_KEY
        benevity.company_id = BENEVITY_COMPANY_ID

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, **kwargs):
        """

        :param request:
        :return:
        """
        event = self.get_object()
        if event.exists():
            receipt = benevity.get_receipt_pdf(receipt=kwargs['receipt_id'])
            return Response({'pdf': base64.encodestring(receipt)}, status=status.HTTP_200_OK)
        return Response('You are not allow to access this information',
                        status=status.HTTP_403_FORBIDDEN)

    def get_object(self):
        return Event.objects.filter(user_event__user=self.request.user.id,
                                    receipt_id=str(self.kwargs['receipt_id']))
