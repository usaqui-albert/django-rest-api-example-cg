from django.http import HttpResponse
from rest_framework import permissions, views

from ConnectGood.settings import BENEVITY_API_KEY, BENEVITY_COMPANY_ID
from benevity_library import benevity


class BenevityReceiptView(views.APIView):
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
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'
        receipt = benevity.get_receipt_pdf(receipt='D6399685NT')
        response.write(receipt)
        return response
