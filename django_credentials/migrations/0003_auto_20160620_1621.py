# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_credentials', '0002_auto_20150206_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basecredential',
            name='status',
            field=models.CharField(max_length=255, default='active', choices=[('active', 'Active'), ('deleted', 'Deleted')]),
        ),
        migrations.AlterField(
            model_name='basecredential',
            name='title',
            field=models.CharField(max_length=255, help_text='A descriptive use for this user, e.g. cPanel, CMS, FTP'),
        ),
        migrations.AlterField(
            model_name='basecredential',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='httpuser',
            name='url',
            field=models.URLField(max_length=255, help_text='The login URL for these credentials.'),
        ),
        migrations.AlterField(
            model_name='userpassword',
            name='username',
            field=models.CharField(max_length=255, help_text='Username for this user.'),
        ),
    ]
