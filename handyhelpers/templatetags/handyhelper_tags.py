"""Presentation filters with explicit handling of empty values and safe output."""

from datetime import datetime
from urllib.parse import parse_qsl, urlencode

from django import template
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


def group_names(user):
    return (
        set(user.groups.values_list("name", flat=True))
        if getattr(user, "is_authenticated", False)
        else set()
    )


@register.filter
def has_group(user, group_name):
    return group_name in group_names(user)


@register.filter(name="in")
def inside(value, arg):
    try:
        return value in arg
    except TypeError:
        return False


@register.filter
def add(value, arg):
    return value + arg


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def index(indexable, i):
    try:
        return indexable[int(i)]
    except (IndexError, KeyError, TypeError, ValueError):
        return ""


@register.filter(needs_autoescape=True)
def nbsp(value, autoescape=True):
    escape = conditional_escape if autoescape else str
    return mark_safe("&nbsp;".join(escape(str(value)).split(" ")))


@register.filter
def intcomma(value):
    return f"{value:,}" if value is not None else ""


@register.filter
def usd(value):
    return f"${value:,.2f}" if value is not None else ""


@register.filter
def or_blank(value):
    return "" if value is None else value


@register.filter
def or_zero(value):
    return 0 if value is None else value


@register.filter
def percentage(value):
    if value is None:
        return ""
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return ""


@register.filter(name="title_underscore")
def field_name_to_label(value):
    return str(value).replace("_", " ").title()


@register.filter(name="host_ip_address")
def host_ip_address(value):
    text = str(value)
    if text.startswith("["):
        return text[1 : text.find("]")]
    return text.rsplit(":", 1)[0] if text.count(":") == 1 else text


@register.filter
def inlist(value, value_list):
    values = (
        [item.strip() for item in value_list.split(",")]
        if isinstance(value_list, str)
        else value_list
    )
    return value in values


@register.filter
def in_any_group(user, group_list):
    return bool(group_names(user).intersection(item.strip() for item in group_list.split(",")))


@register.filter
def in_all_groups(user, group_list):
    return {item.strip() for item in group_list.split(",") if item.strip()}.issubset(
        group_names(user)
    )


@register.filter
def get_filtered_pagination_link(page, query_params):
    params = [
        (key, value)
        for key, value in parse_qsl(str(query_params), keep_blank_values=True)
        if key != "page"
    ]
    return urlencode([("page", page), *params])


@register.filter
def get_groups(user):
    return sorted(group_names(user))


@register.filter
def in_any(values, other):
    return bool(set(values).intersection(other.split(",") if isinstance(other, str) else other))


@register.filter(name="next")
def dj_iter(gen):
    return next(gen, None)


@register.filter
def byte_size(value):
    return filesizeformat(value)


@register.filter
def to_datetime(value):
    try:
        result = datetime.fromtimestamp(float(value), tz=timezone.get_current_timezone())
        return result
    except (ValueError, TypeError, OverflowError, OSError):
        return None


@register.filter
def model_label(value):
    return value._meta.label_lower if value is not None else ""
