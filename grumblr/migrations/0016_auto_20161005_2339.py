# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-06 03:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grumblr', '0015_userprofile_is_confirmed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='is_confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
