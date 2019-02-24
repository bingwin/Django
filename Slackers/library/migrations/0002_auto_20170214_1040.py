# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-14 02:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookinfo',
            name='category',
            field=models.CharField(default='\u6587\u5b66', max_length=64),
        ),
        migrations.AlterField(
            model_name='bookinfo',
            name='cover',
            field=models.ImageField(null=True, upload_to=b''),
        ),
        migrations.AlterField(
            model_name='bookinfo',
            name='index',
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='bookinfo',
            name='location',
            field=models.CharField(default='\u56fe\u4e66\u99861\u697c', max_length=64),
        ),
    ]