from __future__ import unicode_literals

import logging
import socket
from unittest.case import TestCase

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.test import FTPd

from ..models import UserPassword, FtpUser

class EncryptedFieldTestCase(TestCase):

    def test_has_encrypt_field(self):
        self.assertTrue(hasattr(UserPassword(), 'encrypt_password'))

    def test_has_decrypt_field(self):
        self.assertTrue(hasattr(UserPassword(), 'decrypt_password'))

    def test_encrypt_field(self):
        u = UserPassword()
        u.encrypt_password('asdf')

    def test_decrypt_field(self):
        u = UserPassword()
        u.encrypt_password('asdf')
        self.assertEqual(u.decrypt_password(), 'asdf')

    def test_get_field_by_name(self):
        UserPassword._meta.get_field_by_name('password')


class FtpUserTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        logging.disable(logging.INFO)
        cls.server = FTPd()
        authorizer = DummyAuthorizer()
        authorizer.add_user('ok', 'p@ss', '.', perm='')
        cls.server.handler.authorizer = authorizer
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        logging.disable(logging.NOTSET)

    def assert_attributes_equal(self, lhs, **kwargs):
        for k in kwargs:
            actual = getattr(lhs, k)
            if callable(actual):
                actual = actual()
                label = '() method'
            else:
                label = ' field'
            self.assertEquals(actual, kwargs[k],
                              '{}{} of {!r}'.format(k, label, lhs))

    def test_create_from_url_with_no_auth(self):
        with self.assertRaisesRegexp(ValueError,
                '^username and password required$'):
            FtpUser.objects.create_from_url('ftp://127.0.0.1:50913/')

    def test_create_from_url_with_http(self):
        with self.assertRaisesRegexp(ValueError,
                "^unknown scheme 'http' \(known schemes: ftp, ftps, sftp\)$"):
            FtpUser.objects.create_from_url('http://user:pass@host/')

    def test_create_from_url_1(self):
        f = FtpUser.objects.create_from_url('ftp://u:p@127.0.0.1:50913/', 'foo')
        self.assert_attributes_equal(
            f,
            protocol='ftp', host='127.0.0.1', port=50913, username='u',
            decrypt_password='p',
            as_url='ftp://u:p@127.0.0.1:50913/',
            __str__='foo: ftp://u:p@127.0.0.1:50913/')

    def test_create_from_url_2(self):
        f = FtpUser.objects.create_from_url('ftps://username:p%40ssword@host/')
        self.assert_attributes_equal(
            f,
            protocol='ftps', host='host', port=990, username='username',
            decrypt_password='p@ssword',
            as_url='ftps://username:p%40ssword@host/',
            __str__='FTP details for host: ftps://username:p%40ssword@host/')

    def test_silly_httpness(self):
        f = FtpUser(host='http://example.com/', port=21, username='foo')
        f.encrypt_password('bar')
        f.title = 'http details for example.com'
        f.save()
        self.assert_attributes_equal(
            f,
            protocol='http', host='http://example.com/', port=21,
            username='foo', decrypt_password='bar',
            as_url='http://example.com/',
            __str__='http details for example.com: http://example.com/')

    def test_verify_success(self):
        f = FtpUser.objects.create_from_url('ftp://ok:p%40ss@127.0.0.1/')
        f.port = self.server.port
        f.verify(timeout=5)
        self.assertTrue(f.verified)
        self.assertRegex(f.verification_message, '220 pyftpdlib \S+ ready.\n'
                                                 '230 Login successful.')

    def test_verify_bad_login(self):
        f = FtpUser.objects.create_from_url('ftp://no:p%40ss@127.0.0.1/')
        f.port = self.server.port
        f.verify(timeout=5)
        self.assertFalse(f.verified)
        self.assertRegex(f.verification_message, '220 pyftpdlib \S+ ready.\n'
                                                 '530 Authentication failed.')

    def test_verify_bad_connect(self):
        # Select a port that is not in use. Slight race condition here; meh.
        s = socket.socket()
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()

        f = FtpUser.objects.create_from_url('ftp://u:p@127.0.0.1/')
        f.port = port
        f.verify(timeout=5)
        self.assertFalse(f.verified)
        self.assertEquals(f.verification_message,
                          '[Errno 111] Connection refused')

    # FIXME: there is no FTPS verification testing (can be done with
    # pyftpdlib.handlers.TLS_FTPHandler, just needs certificate and all)

    # FIXME: there is no SFTP verification testing (need something like
    # pyftpdlib but for SFTP)

    def test_verify_on_silly_httpness(self):
        f = FtpUser(host='http://example.com/', port=21, username='foo')
        f.encrypt_password('bar')
        f.save()
        f.verify(timeout=5)
        self.assertFalse(f.verified)
        self.assertEquals(f.verification_message,
                          "bad data: 'http://example.com/' isn't FTP "
                          "and so shouldn't be here")


if not hasattr(FtpUserTestCase, 'assertRegex'):
    # It was renamed to assertRegex in Python 3.2, I like that name better.
    FtpUserTestCase.assertRegex = TestCase.assertRegexpMatches
