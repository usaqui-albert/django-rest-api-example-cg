from django.db import models

class Country(models.Model):
    """Model for Country Object"""
    name = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
