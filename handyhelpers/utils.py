"""Shared request, URL, and optional dependency helpers."""

from importlib import import_module
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.utils.http import url_has_allowed_host_and_scheme

DEFAULT_BASE_TEMPLATE = "handyhelpers/handyhelpers_base_bs5.htm"


def optional_import(module, extra):
    try:
        return import_module(module)
    except ModuleNotFoundError as error:
        if error.name != module.split(".")[0]:
            raise
        raise ImproperlyConfigured(
            f"This feature requires django-handyhelpers[{extra}]. "
            f"Install it with: pip install 'django-handyhelpers[{extra}]'"
        ) from error


def base_template_name(override=None):
    return override or getattr(settings, "BASE_TEMPLATE", DEFAULT_BASE_TEMPLATE)


def update_query(url, parameters, replace=False):
    parts = urlsplit(url)
    values = [] if replace else parse_qsl(parts.query, keep_blank_values=True)
    values = [(key, value) for key, value in values if key not in parameters]
    values.extend((key, value) for key, value in parameters.items() if value is not None)
    return urlunsplit(parts._replace(query=urlencode(values, doseq=True)))


def safe_return_url(request, fallback="/"):
    url = request.META.get("HTTP_REFERER", "")
    if url_has_allowed_host_and_scheme(
        url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return url
    return fallback


class InvalidFilter(ValueError):
    """A supplied filter is not a valid model lookup/value."""


class RequestStateMixin:
    """Copy mutable configuration without evaluating configured querysets."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for name in ("context", "data", "extra_data", "extra_controls"):
            value = getattr(self, name, None)
            if value is not None:
                setattr(self, name, self._copy_config(value))

    @classmethod
    def _copy_config(cls, value):
        if isinstance(value, dict):
            return {key: cls._copy_config(item) for key, item in value.items()}
        if isinstance(value, list):
            return [cls._copy_config(item) for item in value]
        if isinstance(value, tuple):
            return tuple(cls._copy_config(item) for item in value)
        if isinstance(value, set):
            return value.copy()
        return value

    def dispatch(self, request, *args, **kwargs):
        try:
            response = super().dispatch(request, *args, **kwargs)
        except InvalidFilter as error:
            return HttpResponseBadRequest(str(error))
        if hasattr(self, "is_htmx"):
            from django.utils.cache import patch_vary_headers

            patch_vary_headers(response, ["HX-Request"])
        return response
