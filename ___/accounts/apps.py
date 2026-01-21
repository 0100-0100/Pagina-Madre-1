import sys

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Python 3.14 compatibility patch for Django 4.2
        # Django's BaseContext.__copy__ uses copy(super()) which fails in Python 3.14
        # because super() objects no longer have __dict__ for copying
        # Must be applied in ready() after Django is fully initialized
        if sys.version_info >= (3, 14):
            from django.template import context as django_context

            def _patched_base_context_copy(self):
                """Patched BaseContext.__copy__ that works with Python 3.14+"""
                duplicate = object.__new__(type(self))
                duplicate.__dict__.update(self.__dict__)
                duplicate.dicts = self.dicts[:]
                return duplicate

            django_context.BaseContext.__copy__ = _patched_base_context_copy

        # Import signals to register handlers
        from . import signals  # noqa: F401
