# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('focus', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='newuser',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='article',
            name='column',
            field=models.ForeignKey(verbose_name='belong to', blank=True, null=True, to='focus.Column'),
        ),
        migrations.AlterField(
            model_name='article',
            name='content',
            field=models.TextField(verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='article',
            name='published',
            field=models.BooleanField(verbose_name='notDraft', default=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='password',
            field=models.CharField(verbose_name='password', max_length=256),
        ),
        migrations.AlterField(
            model_name='author',
            name='profile',
            field=models.CharField(verbose_name='profile', max_length=256, default=''),
        ),
        migrations.AlterField(
            model_name='column',
            name='intro',
            field=models.TextField(verbose_name='introduction', default=''),
        ),
        migrations.AlterField(
            model_name='column',
            name='name',
            field=models.CharField(verbose_name='column_name', max_length=256),
        ),
        migrations.AlterField(
            model_name='newuser',
            name='profile',
            field=models.CharField(verbose_name='profile', max_length=256, default=''),
        ),
    ]
