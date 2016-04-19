#!/usr/bin/env python
import sys

from django.conf import settings
from django.core.management import execute_from_command_line


if not settings.configured:
    settings.configure(
        INSTALLED_APPS=('django_credentials',),
        # Django replaces this, but it still wants it. *shrugs*
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
    )


def runtests():
    test_args = sys.argv[1:] if len(sys.argv[1:]) > 0 else ['django_credentials.tests']
    argv = sys.argv[:1] + ['test'] + test_args
    execute_from_command_line(argv)


if __name__ == '__main__':
    runtests()
