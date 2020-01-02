from django import template
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        return group in user.groups.all()
    except:
        return None


@register.filter(name='in')
def inside(value, arg):
    try:
        return value in arg
    except:
        return None


@register.filter
def add(value, arg):
    if arg:
        return value + arg


@register.filter
def subtract(value, arg):
    if arg:
        return value - arg


@register.filter()
def nbsp(value):
    return mark_safe("&nbsp;".join(value.split(' ')))


@register.filter
def intcomma(value):
    if value:
        return "{:,}".format(value)
    else:
        return 0


@register.filter
def usd(value):
    if value:
        return "${0:,.2f}".format(value)
    else:
        return 0


@register.filter
def or_blank(value):
    """ return an empty string if value is None """
    if value:
        return value
    else:
        return ""


@register.filter
def or_zero(value):
    """ return a zero if value is None """
    if value:
        return value
    else:
        return 0


@register.filter(name='percentage')
def percentage(value):
    if not value:
        return ""
    try:
        return "{:4.2f}%".format(float(value)*100)
    except:
        return ""
