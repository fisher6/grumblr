# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-16 01:11
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grumblr', '0023_auto_20161015_2052'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('date',)},
        ),
    ]
