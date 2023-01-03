import re
import datetime

from hurry.filesize import size

from django import template
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    """
    {% if request.user|has_group:"mygroup" %}
        <p>User belongs to my group
    {% else %}
        <p>User doesn't belong to mygroup</p>
    {% endif %}
    """
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


@register.filter
def index(indexable, i):
    return indexable[i]


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


@register.filter(name='title_underscore')
def field_name_to_label(value):
    value = value.replace('_', ' ')
    return value.title()


@register.filter(name='host_ip_address')
def host_ip_address(value):
    return value.split(':')[0]


@register.filter(name='inlist')
def inlist(value, value_list):
    """
    return True if value is in a 'list' of values

        usage:
            {% value|inlist:"val1,val2,val3" %}

    Args:
        value: (str) value to check
        value_list: (str) comma separated values

    Returns:
        True if value in value_list, otherwise False
    """
    return True if value in value_list else False


@register.filter(name='in_any_group')
def in_any_group(user, group_list):
    """
    return True if user is in at least one group defined in 'list'

        usage:
            {% if request.user|in_any_group:"admins,operators,users" %}

    Args:
        user: user object
        group_list: (str) comma separated values

    Returns:
        True if user is in at least one group defined in 'group_list' otherwise False
    """
    return any(group in [i.name for i in user.groups.all()] for group in group_list.split(','))


@register.filter(name='in_all_group')
def in_all_groups(user, group_list):
    """
    return True if user is in all groups defined in 'list'

        usage:
            {% if request.user|in_all_groups:"admins,operators,users" %}

    Args:
        user: user object
        group_list: (str) comma separated values

    Returns:
        True if user is in all groups defined in 'group_list' otherwise False
    """
    return set(group_list.split(',')).issubset([i.name for i in user.groups.all()])


@register.filter(name='get_filtered_pagination_link')
def get_filtered_pagination_link(page, query_params):
    """
    return the paginated link with (filter) query parameters included
        usage example:
            <a href="?page={{ page_obj.paginator.num_pages|get_filtered_pagination_link:request.META.QUERY_STRING }}">

    Args:
        page: page number (probably from paginator)
        query_params: request query string
    """
    query_params = str(query_params)
    match = re.search('^page=\d+(.*)$', query_params)
    if match:
        filter_string = match.groups()[0]
        if not filter_string:
            return page
        return f'{page}{filter_string}'
    else:
        return f'{page}&{query_params}'
    return page


@register.filter(name='get_groups')
def get_groups(user):
    """
    Args:
        user: django user object

    Returns:
        list of group names representing all groups user is a member of
    """
    try:
        return [group.name for group in user.groups.all()]
    except Exception:
        return []


@register.filter(name='in_any')
def in_any(l1, l2):
    """
    checks if there is any intersection of two lists
    Args:
        l1: list
        l2: list

    Returns:
        True if there is at least one intersection; otherwise False
    """
    return True if set(l1).intersection(l2.split(',')) else False


@register.filter(name='next')
def dj_iter(gen):
    """
    return the next value as yielded from a generator
    Args:
        gen: generator object

    Returns:
        value as yielded from generator
    """
    try:
        return next(gen)
    except StopIteration:
        return None


@register.filter(name='byte_size')
def byte_size(value):
    try:
        return size(value)
    except:
        return None


@register.filter(name='to_datetime')
def to_datetime(value):
    try:
        return datetime.datetime.fromtimestamp(value)
    except:
        return None


@register.filter
def model_label(value):
    if value:
        return value._meta.label_lower
    else:
        return 0
