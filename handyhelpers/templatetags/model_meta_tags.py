from django import template

register = template.Library()


@register.filter
def app_label(value):
    if value:
        return value._meta.app_label
    else:
        return 0


@register.filter
def db_table(value):
    if value:
        return value._meta.db_label
    else:
        return 0


@register.filter
def label(value):
    if value:
        return value._meta.label
    else:
        return 0


@register.filter
def label_lower(value):
    if value:
        return value._meta.label_lower
    else:
        return 0


@register.filter
def model_name(value):
    if value:
        return value._meta.model_name
    else:
        return 0


@register.filter
def object_name(value):
    if value:
        return value._meta.object_name
    else:
        return 0


@register.filter
def verbose_name(value):
    if value:
        return value._meta.verbose_name
    else:
        return 0


@register.filter
def verbose_name_plural(value):
    if value:
        return value._meta.verbose_name_plural
    else:
        return 0


@register.filter
def verbose_name_raw(value):
    if value:
        return value._meta.verbose_name_raw
    else:
        return 0
