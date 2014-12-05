# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'BaseCredential.last_verified'
        db.add_column(u'django_credentials_basecredential', 'last_verified',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BaseCredential.verified'
        db.add_column(u'django_credentials_basecredential', 'verified',
                      self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'BaseCredential.verification_message'
        db.add_column(u'django_credentials_basecredential', 'verification_message',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'BaseCredential.last_verified'
        db.delete_column(u'django_credentials_basecredential', 'last_verified')

        # Deleting field 'BaseCredential.verified'
        db.delete_column(u'django_credentials_basecredential', 'verified')

        # Deleting field 'BaseCredential.verification_message'
        db.delete_column(u'django_credentials_basecredential', 'verification_message')


    models = {
        u'django_credentials.basecredential': {
            'Meta': {'object_name': 'BaseCredential'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_verified': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'verification_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'verified': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        u'django_credentials.ftpuser': {
            'Meta': {'object_name': 'FtpUser', '_ormbases': [u'django_credentials.UserPassword']},
            'host': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'port': ('django.db.models.fields.IntegerField', [], {'default': '21'}),
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