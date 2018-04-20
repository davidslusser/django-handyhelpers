"""
Description:
    Collection of helpers to assist with queryset operations

"""

# import system modules
import datetime
import collections

# import Django modules
from django.db.models import Count
from django.utils import timezone


def count_by_hour(queryset, field_name):
    """
    Description:
        sort queryset results by hour of day

    Parameters:
        queryset   - django queryset
        field_name - field to group data by (string)

    Returns:
        list of grouped values: count of entries per hour, starting with current hour, descending chronologically
    """
    data = queryset.extra({'hour': "hour({})".format(field_name)}).values('hour').annotate(Count('id'))
    new_dict = collections.OrderedDict()
    for i in data:
        values = i.values()
        new_dict[values[0]] = values[1]

    return_list = []
    now = timezone.now()
    for i in [(now - datetime.timedelta(hours=i)).hour for i in range(0, 24)]:
        if i not in new_dict.keys():
            return_list.append(0)
        else:
            return_list.append(new_dict[i])
    return return_list


def count_by_week(queryset, field_name):
    """
    Description:
        sort queryset results by week of year

    Parameters:
        queryset   - django queryset
        field_name - field to group data by (string)

    Returns:
        list of grouped values
        list of grouped values: count of entries per week, starting with current week, descending chronologically
    """
    data = queryset.extra({'week': "week({})".format(field_name)}).values('week').annotate(Count('id'))
    new_dict = collections.OrderedDict()
    for i in data:
        new_dict[i['week']] = i['id__count']

    return_list = []
    now = timezone.now()
    for i in [(now - datetime.timedelta(weeks=i)).isocalendar()[1] for i in range(0, 52)]:
        if i not in new_dict.keys():
            return_list.append(0)
        else:
            return_list.append(new_dict[i])
    return return_list


def count_by_month(queryset, field_name):
    """
    Description:
        sort queryset results by month of year

    Parameters:
        queryset   - django queryset
        field_name - field to group data by (string)

    Returns:
        list of grouped values: count of entries per month, starting with current month, descending chronologically
    """
    data = queryset.extra({'month': "month({})".format(field_name)}).values('month').annotate(Count('id'))
    new_dict = collections.OrderedDict()
    for i in data:
        new_dict[i['month']] = i['id__count']

    return_list = []
    now = timezone.now()
    for i in [(now - datetime.timedelta(i * 365 / 12)).month for i in range(0, 12)]:
        if i not in new_dict.keys():
            return_list.append(0)
        else:
            return_list.append(new_dict[i])
    return return_list
