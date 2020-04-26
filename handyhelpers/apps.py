from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.fields import Field
from handyhelpers.lookups import NotEqual


class HandyHelpersConfig(AppConfig):
    name = 'handyhelpers'
    verbose_name = "django-handyhelpers"

    def ready(self):
        # register field lookups
        Field.register_lookup(NotEqual)
