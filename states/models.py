from django.db import models
from countries.models import Country

class State(models.Model):
    """Model for State/Province Object"""
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, related_name='states')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
