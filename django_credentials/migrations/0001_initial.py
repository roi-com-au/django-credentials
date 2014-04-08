# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EncryptedModel'
        db.create_table(u'django_credentials_encryptedmodel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'django_credentials', ['EncryptedModel'])

        # Adding model 'BaseCredential'
        db.create_table(u'django_credentials_basecredential', (
            (u'encryptedmodel_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['django_credentials.EncryptedModel'], unique=True, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=255)),
        ))
        db.send_create_signal(u'django_credentials', ['BaseCredential'])

        # Adding model 'UserPassword'
        db.create_table(u'django_credentials_userpassword', (
            (u'basecredential_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['django_credentials.BaseCredential'], unique=True, primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('password', self.gf('django_credentials.fields.EncryptedField')()),
        ))
        db.send_create_signal(u'django_credentials', ['UserPassword'])

        # Adding model 'FtpUser'
        db.create_table(u'django_credentials_ftpuser', (
            (u'userpassword_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['django_credentials.UserPassword'], unique=True, primary_key=True)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('port', self.gf('django.db.models.fields.IntegerField')(default=22)),
        ))
        db.send_create_signal(u'django_credentials', ['FtpUser'])

        # Adding model 'HttpUser'
        db.create_table(u'django_credentials_httpuser', (
            (u'userpassword_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['django_credentials.UserPassword'], unique=True, primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255)),
        ))
        db.send_create_signal(u'django_credentials', ['HttpUser'])


    def backwards(self, orm):
        # Deleting model 'EncryptedModel'
        db.delete_table(u'django_credentials_encryptedmodel')

        # Deleting model 'BaseCredential'
        db.delete_table(u'django_credentials_basecredential')

        # Deleting model 'UserPassword'
        db.delete_table(u'django_credentials_userpassword')

        # Deleting model 'FtpUser'
        db.delete_table(u'django_credentials_ftpuser')

        # Deleting model 'HttpUser'
        db.delete_table(u'django_credentials_httpuser')


    models = {
        u'django_credentials.basecredential': {
            'Meta': {'object_name': 'BaseCredential', '_ormbases': [u'django_credentials.EncryptedModel']},
            u'encryptedmodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['django_credentials.EncryptedModel']", 'unique': 'True', 'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'django_credentials.encryptedmodel': {
            'Meta': {'object_name': 'EncryptedModel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'django_credentials.ftpuser': {
            'Meta': {'object_name': 'FtpUser', '_ormbases': [u'django_credentials.UserPassword']},
            'host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '22'}),
            u'userpassword_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['django_credentials.UserPassword']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'django_credentials.httpuser': {
            'Meta': {'object_name': 'HttpUser', '_ormbases': [u'django_credentials.UserPassword']},
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            u'userpassword_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['django_credentials.UserPassword']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'django_credentials.userpassword': {
            'Meta': {'object_name': 'UserPassword', '_ormbases': [u'django_credentials.BaseCredential']},
            u'basecredential_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['django_credentials.BaseCredential']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django_credentials.fields.EncryptedField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['django_credentials']