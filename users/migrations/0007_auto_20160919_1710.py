# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-19 17:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_user_free_trial_started_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='company',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
