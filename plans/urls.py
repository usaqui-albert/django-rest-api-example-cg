from django.conf.urls import url
from .views import InvoiceView, InvoiceDetail

urlpatterns = [
    url(r'^$', InvoiceView.as_view()),
    url(r'^(?P<invoice_id>[0-9A-Za-z_]+)/$', InvoiceDetail.as_view())

]
