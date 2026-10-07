from django.apps import AppConfig
from django.conf import settings
from django.db.models.fields import Field
from django.utils import timezone

from handyhelpers.lookups import NotEqual


class HandyHelpersConfig(AppConfig):
    name = "handyhelpers"
    default_auto_field = "django.db.models.AutoField"
    verbose_name = "django-handyhelpers"

    def ready(self):
        Field.register_lookup(NotEqual)
        settings.HH_STARTTIME = timezone.now()
