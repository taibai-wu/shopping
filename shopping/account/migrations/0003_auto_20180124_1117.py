# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-24 03:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_userext_verification_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userext',
            name='verification_time',
            field=models.IntegerField(default=1516764453.1426702),
        ),
    ]