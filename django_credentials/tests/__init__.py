from unittest.case import TestCase
from django_credentials.models import UserPassword

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
