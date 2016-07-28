# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-27 18:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('countries', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userevent',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_event', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_country', to='countries.Country'),
        ),
    ]
