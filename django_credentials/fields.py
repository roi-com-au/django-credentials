from django.db import models
from django.utils.functional import curry

class EncryptedField(models.TextField):

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(EncryptedField, self).contribute_to_class(cls, name, virtual_only)
        setattr(cls, 'encrypt_%s' % self.name, curry(cls._encrypt_FIELD, field=self))
        setattr(cls, 'decrypt_%s' % self.name, curry(cls._decrypt_FIELD, field=self))

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^django_credentials\.fields\.EncryptedField"])
except ImportError: pass