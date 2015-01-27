# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_credentials.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseCredential',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text=b'A descriptive use for this user, ie.. cPanel, CMS, FTP etc..', max_length=255)),
                ('status', models.CharField(default=b'active', max_length=255, choices=[(b'active', b'Active'), (b'deleted', b'Deleted')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True, auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserPassword',
            fields=[
                ('basecredential_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='django_credentials.BaseCredential')),
                ('username', models.CharField(help_text=b'Username for this user.', max_length=255)),
                ('password', django_credentials.fields.EncryptedField()),
            ],
            options={
                'abstract': False,
            },
            bases=('django_credentials.basecredential',),
        ),
        migrations.CreateModel(
            name='HttpUser',
            fields=[
                ('userpassword_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='django_credentials.UserPassword')),
                ('url', models.URLField(help_text=b'The login url for these credentials.', max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('django_credentials.userpassword',),
        ),
        migrations.CreateModel(
            name='FtpUser',
            fields=[
                ('userpassword_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='django_credentials.UserPassword')),
                ('host', models.CharField(max_length=255)),
                ('port', models.IntegerField(default=22)),
            ],
            options={
                'abstract': False,
            },
            bases=('django_credentials.userpassword',),
        ),
    ]
