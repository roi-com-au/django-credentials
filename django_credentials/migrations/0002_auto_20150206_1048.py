# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_credentials', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='basecredential',
            name='last_verified',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basecredential',
            name='verification_message',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basecredential',
            name='verified',
            field=models.NullBooleanField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ftpuser',
            name='port',
            field=models.IntegerField(default=21),
            preserve_default=True,
        ),
    ]
