from typing import Any

from django.conf import settings

from handyhelpers.utils import base_template_name


def base_template(request) -> dict[str, Any | str]:
    return {"BASE_TEMPLATE": base_template_name(), "base_template": base_template_name()}


def get_settings(request) -> dict[str, Any | str]:
    return {
        **base_template(request),
        "PROJECT_NAME": getattr(settings, "PROJECT_NAME", ""),
        "PROJECT_VERSION": getattr(settings, "PROJECT_VERSION", ""),
        "HH_STARTTIME": getattr(settings, "HH_STARTTIME", ""),
        "GOOGLE_ANALYTICS_TAG_ID": getattr(settings, "GOOGLE_ANALYTICS_TAG_ID", None),
    }


def google_analytics(request) -> dict[str, Any | str]:
    return {"GOOGLE_ANALYTICS_TAG_ID": getattr(settings, "GOOGLE_ANALYTICS_TAG_ID", None)}
