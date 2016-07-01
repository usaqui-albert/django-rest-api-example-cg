from django.db import models

from countries.models import Country

class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, related_name='countries')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
