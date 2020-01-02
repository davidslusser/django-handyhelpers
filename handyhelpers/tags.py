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
def math_add(value, arg):
    if arg:
        return value + arg


@register.filter
def math_subtract(value, arg):
    if arg:
        return value - arg


@register.filter()
def nbsp(value):
    """ allow blank spaces in value """
    return mark_safe("&nbsp;".join(value.split(' ')))


@register.filter
def intcomma(value):
    """ return thousand-separated formatted representation of value """
    if value:
        return "{:,}".format(value)


@register.filter
def currency_usd(value):
    """ return currency (USD) formatted representation of value """
    if value:
        return "${0:,.2f}".format(value)
