from __future__ import unicode_literals
from os import urandom
import ftplib
from base64 import b64encode, b64decode
from django.utils.http import urlquote, urlunquote, urlparse

from celery.contrib.methods import task
from Crypto.Cipher import ARC4
from django.conf import settings
from django.db import models
from django.utils import timezone
from model_utils.managers import InheritanceManager
import pysftp

from .fields import EncryptedField


class EncryptedModel(models.Model):
    SALT_SIZE = 8

    class Meta:
        abstract = True

    def encrypt(self, raw):
        salt = urandom(self.SALT_SIZE)
        arc4 = ARC4.new(salt + settings.SECRET_KEY.encode('utf8'))
        raw = raw.encode('utf8')
        raw = b'%3d%s%s' % (len(raw), raw, urandom(256 - len(raw)))
        return b'%s$%s' % (b64encode(salt), b64encode(arc4.encrypt(raw)))

    def decrypt(self, ciphertext):
        salt, ciphertext = map(b64decode, ciphertext.split(b'$'))
        arc4 = ARC4.new(salt + settings.SECRET_KEY.encode('utf8'))
        plaintext = arc4.decrypt(ciphertext)
        return plaintext[3:3 + int(plaintext[:3].strip())].decode('utf8')

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

    title = models.CharField(max_length=255,
                             help_text='A descriptive use for this user, '
                                       'e.g. cPanel, CMS, FTP')
    status = models.CharField(max_length=255, choices=STATUS_CHOICES,
                              default=STATUS_ACTIVE)
    last_verified = models.DateTimeField(null=True, blank=True)
    verified = models.NullBooleanField(null=True, blank=True)
    verification_message = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = InheritanceManager()

    def __unicode__(self):
        return str(self)

    def __str__(self):
        return '{}'.format(self.title)

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
    username = models.CharField(max_length=255,
                                help_text='Username for this user.')
    password = EncryptedField()


class FtpUserManager(models.Manager):
    """The default manager for :class:`FtpUser`."""

    def create_from_url(self, url, title=None):
        """
        Create an FtpUser instance from a URL.

        The scheme, username, password, host and port are extracted from the
        URL; any path data, query string and hash are ignored.

        A title is, if not specified, constructed from the scheme and host.

        Here are a couple of examples:

        >>> f = FtpUser.objects.create_from_url(
        ...     'ftp://username:password@host:12345/this/part?gets#ignored',
        ...     'Fancy title')
        >>> f
        <FtpUser: Fancy title>
        >>> f.host, f.port, f.username, f.decrypt_password()
        ('host', 12345, 'username', 'password')
        >>> f.as_url()
        'ftp://username:password@host:12345'

        >>> f = FtpUser.objects.create_from_url(
        ...     'sftp://wow%3A:p%40ssword@host')
        >>> f
        <FtpUser: SFTP credentials for host>
        >>> f.host, f.port, f.username, f.decrypt_password()
        ('host', 22, 'wow!', 'p@ssword')
        >>> f.as_url()
        'sftp://wow%3A:p%40ssword@host'

        :param url str:
        :raises ValueError: if a URL with no or an unknown scheme is given
                            (ftp, ftps and sftp are the known schemes), or
                            if the port in the URL is non-numeric
        """
        url = urlparse(url)

        if url.scheme == 'ftp':
            port = 21
        elif url.scheme == 'ftps':
            port = 990
        elif url.scheme == 'sftp':
            port = 22
        elif url.scheme == '':
            raise ValueError('URL has no scheme')
        else:
            raise ValueError("unknown scheme '{}' (known schemes: "
                             'ftp, ftps, sftp)'.format(url.scheme))

        if '@' in url.netloc:
            username, host = url.netloc.split('@', 1)
            if ':' in username:
                username, password = username.split(':', 1)
                username = urlunquote(username)
                password = urlunquote(password)
            else:
                username = urlunquote(username)
                password = None
        else:
            username = password = None
            host = url.netloc

        if username is None or password is None:
            raise ValueError('username and password required')

        if ':' in host:
            host, port = host.split(':', 1)
            port = int(port)

        if title is None:
            title = '{protocol} details for {host}'.format(
                protocol={'ftps': 'FTP'}.get(url.scheme, url.scheme.upper()),
                host=host)

        instance = self.model(title=title, host=host, port=port,
                              username=username)
        instance.encrypt_password(password)
        instance.save()
        return instance


class FtpUser(UserPassword):
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=21)

    objects = FtpUserManager()

    def __str__(self):
        return '{}: {}'.format(self.title, self.as_url())

    @task
    def verify(self, timeout=15):
        """Verify the FTP details."""
        processed_host = (self.host.replace('sftp://', '')
                                   .replace('ftp://', '')
                                   #.replace('www.', '')
                                   .replace('https://', '')
                                   .replace('http://', '')
                                   .strip())
        protocol = self.protocol
        if protocol in ('ftp', 'ftps'):
            f = self._verify_ftp
        elif protocol == 'sftp':
            f = self._verify_sftp
        else:
            f = self._verify_spurious

        self.verified, self.verification_message = f(processed_host, timeout)
        self.last_verified = timezone.now()
        self.save(update_fields=['verified', 'verification_message',
                                 'last_verified'])

    def _verify_sftp(self, host, timeout):
        try:
            # TODO: support private keys for SFTP somehow. Easiest way is
            # probably putting it as the password and making username *truly*
            # optional and detecting it in some way. Then you get the issue of
            # openssh/putty format, and so on and so on.
            pysftp.Connection(host=host,
                              username=self.username,
                              password=self.decrypt_password(),
                              port=int(self.port))
        except Exception as e:
            return False, '{}'.format(e)
        else:
            return True, None

    def _verify_ftp(self, host, timeout):
        # We try FTP + TLS first, then plain FTP if that fails.
        message = ['']

        def attempt(f):
            message[0] = f.connect(host, port=int(self.port), timeout=timeout)
            message[0] += '\n'
            message[0] += f.login(self.username, self.decrypt_password())
            return True, message[0]

        try:
            return attempt(ftplib.FTP_TLS())
        except Exception as e:
            try:
                return attempt(ftplib.FTP())
            except Exception as e:
                return False, '{}{}'.format(message[0], e)

    def _verify_spurious(self, host, timeout):
        return (False, "bad data: '{}' isn't FTP and so shouldn't be here"
                .format(self.host))

    @property
    def protocol(self):
        """
        Should return 'ftp', 'ftps' or 'sftp', but can return other values if
        the host is instead a URL with a different scheme.
        """

        if '://' in self.host:
            scheme, host = self.host.split('://', 1)
            return scheme
        elif self.port == 21:
            return 'ftp'
        elif self.port == 22:
            return 'sftp'
        elif self.port == 990:
            return 'ftps'
        else:
            # Uncertain, assume FTP.
            return 'ftp'

    def as_url(self):
        """
        ``self`` as a URL, including the username and password where possible.
        """

        if self.host.startswith(('http://', 'https://')):
            # Some persons have put HTTP details in an FtpUser. At least
            # partially any UI's fault, though still their fault...
            return self.host

        protocol, port, host = self.protocol, self.port, self.host

        if '://' in host:
            host = host.split('://', 1)[1]
            if '@' in host:
                # Probably already has the username and password embedded.
                # Sensible, I'd say, if contrary to the design of this thing.
                return self.host
            if ':' in host:
                host, port = host.split(':', 1)
            else:
                port = None
        else:
            protocol, port, host = self.protocol, self.port, self.host

        if (protocol, port) in (('ftp', 21), ('sftp', 22), ('ftps', 990)):
            port = None

        username = self.username
        password = self.decrypt_password()
        return '{scheme}://{auth}{host}{port}/'.format(
            scheme=protocol,
            auth='{}:{}@'.format(urlquote(username), urlquote(password))
                 if username or password else '',
            host=host,
            port=':{}'.format(port) if port else '')


class HttpUser(UserPassword):
    url = models.URLField(max_length=255,
                          help_text='The login URL for these credentials.')
