# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-23 06:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default', '0008_auto_20161223_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='time',
            field=models.CharField(max_length=20),
        ),
    ]
