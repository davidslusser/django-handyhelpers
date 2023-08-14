from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings
from django.db.models.fields import Field
from django.utils import timezone

from handyhelpers.lookups import NotEqual

from .checks import user_tags_depreciated


class HandyHelpersConfig(AppConfig):
    name = "handyhelpers"
    verbose_name = "django-handyhelpers"

    def ready(self):
        Field.register_lookup(NotEqual)
        settings.HH_STARTTIME = timezone.now()
