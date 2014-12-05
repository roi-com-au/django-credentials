import ftplib
import pysftp
from model_utils.managers import InheritanceManager
from os import urandom
from base64 import b64encode, b64decode
from django.db import models
from Crypto.Cipher import ARC4
from django.conf import settings
from django.utils.functional import curry
from django_credentials.fields import EncryptedField
from django_toolkit.font_awesome import Button, Icon
from celery.contrib.methods import task
from django.utils import timezone


class EncryptedModel(models.Model):
    SALT_SIZE = 8

    class Meta:
        abstract = True

    def encrypt(self, raw):
        salt = urandom(self.SALT_SIZE)
        arc4 = ARC4.new(salt + settings.SECRET_KEY)
        raw = "%3d%s%s" % (len(raw), raw, urandom(256 - len(raw)))
        return "%s$%s" % (b64encode(salt), b64encode(arc4.encrypt(raw)))

    def decrypt(self, ciphertext):
        salt, ciphertext = map(b64decode, ciphertext.split('$'))
        arc4 = ARC4.new(salt + settings.SECRET_KEY)
        plaintext = arc4.decrypt(ciphertext)
        return plaintext[3:3 + int(plaintext[:3].strip())]

    def _encrypt_FIELD(self, raw, field):
        setattr(self, field.name, self.encrypt(raw))

    def _decrypt_FIELD(self, field):
        return self.decrypt(getattr(self, field.name))


class BaseCredential(EncryptedModel):
    STATUS_ACTIVE = 'active'
    STATUS_DELETED = 'deleted'
    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DELETED, 'Deleted'),
    )

    title = models.CharField(max_length=255, help_text='A descriptive use for this user, ie.. cPanel, CMS, FTP etc..')
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    last_verified = models.DateTimeField(null=True, blank=True)
    verified = models.NullBooleanField(null=True, blank=True)
    verification_message = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=True)

    objects = InheritanceManager()

    def __unicode__(self):
        return '%s' % self.title

    def get_status_label_class(self):
        if self.status == self.STATUS_ACTIVE:
            return 'label-success'
        elif self.status == self.STATUS_DELETED:
            return 'label-important'

    def get_verified_label_class(self):
        if self.verified:
            return 'label-success'
        elif not self.verified:
            return 'label-important'


class UserPassword(BaseCredential):
    username = models.CharField(max_length=255, help_text='Username for this user.')
    password = EncryptedField()


class FtpUser(UserPassword):
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=21)

    @task
    def verify(self):
        """
        Verify the ftp details
        """
        processed_host = self.host.replace('sftp://', '').replace('ftp://', '').replace('www.', '').replace('https://', '').replace('http://', '').strip()

        if 'sftp://' in self.host:
            try:
                c = pysftp.Connection(host=processed_host, username=self.username, password=self.password, port=self.port)
                self.verified = True
                self.last_verified = timezone.now()
                self.save(update_fields=['verified', 'verification_message', 'last_verified'])
            except Exception as e:
                self.verified = False
                self.verification_message = str(e)
                self.last_verified = timezone.now()
                self.save(update_fields=['verified', 'verification_message', 'last_verified'])
        else:
            for pasv in (True, False):
                try:
                    f = ftplib.FTP(user=self.username, passwd=self.password)
                    f.set_pasv(pasv)
                    c = f.connect(host=processed_host, port=self.port, timeout=5)
                    self.verified = True
                    self.verification_message = str(c)
                    break
                except Exception as e:
                    self.verified = False
                    self.verification_message = str(e)

            self.last_verified = timezone.now()
            self.save(update_fields=['verified', 'verification_message', 'last_verified'])

class HttpUser(UserPassword):
    url = models.URLField(max_length=255, help_text='The login url for these credentials.')
