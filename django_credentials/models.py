from django.db import models
from model_utils.managers import InheritanceManager
from os import urandom
from base64 import b64encode, b64decode
from django.db import models
from Crypto.Cipher import ARC4
from django.conf import settings
from django.utils.functional import curry
from django_credentials.fields import EncryptedField

class EncryptedModel(models.Model):
    SALT_SIZE = 8
    
    class Meta:
        abstract = True
    
    def encrypt(self, raw):
        salt = urandom(self.SALT_SIZE)
        arc4 = ARC4.new(salt + settings.SECRET_KEY)
        raw = "%3d%s%s" % (len(raw), raw, urandom(256-len(raw)))
        return "%s$%s" % (b64encode(salt), b64encode(arc4.encrypt(raw)))
        
    def decrypt(self, ciphertext):
        salt, ciphertext = map(b64decode, ciphertext.split('$'))
        arc4 = ARC4.new(salt + settings.SECRET_KEY)
        plaintext = arc4.decrypt(ciphertext)
        return plaintext[3:3+int(plaintext[:3].strip())]

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
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=True)

    objects = InheritanceManager()

    def __unicode__(self):
        return '%s' % self.title

class UserPassword(BaseCredential):
    username = models.CharField(max_length=255, help_text='Username for this user.')
    password = EncryptedField()

class FtpUser(UserPassword):
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=22)

class HttpUser(UserPassword):
    url = models.URLField(max_length=255, help_text='The login url for these credentials.')
