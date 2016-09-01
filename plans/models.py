from django.db import models


class Invoice(models.Model):
    serial_number = models.CharField(max_length=10, null=True)
    stripe_id = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def generate_invoice_number(self):
        x = str(self.pk)
        return '0' * (6 - len(x)) + x
