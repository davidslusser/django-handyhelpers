from typing import Any

from django.conf import settings


def base_template(request) -> dict[str, Any | str]:
    return {
        "BASE_TEMPLATE": getattr(
            settings, "BASE_TEMPLATE", "handyhelpers/handyhelpers_base_bs5.htm"
        )
    }


def get_settings(request) -> dict[str, Any | str]:
    return {
        "BASE_TEMPLATE": getattr(
            settings, "BASE_TEMPLATE", "handyhelpers/handyhelpers_base_bs5.htm"
        ),
        "PROJECT_NAME": getattr(settings, "PROJECT_NAME", ""),
        "PROJECT_VERSION": getattr(settings, "PROJECT_VERSION", ""),
        "HH_STARTTIME": getattr(settings, "HH_STARTTIME", ""),
        "GOOGLE_ANALYTICS_TAG_ID": getattr(settings, "GOOGLE_ANALYTICS_TAG_ID", None),
    }


def google_analytics(request) -> dict[str, Any | str]:
    return {
        "GOOGLE_ANALYTICS_TAG_ID": getattr(settings, "GOOGLE_ANALYTICS_TAG_ID", None)
    }
