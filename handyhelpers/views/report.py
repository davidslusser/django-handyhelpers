from django.views.generic import View
from django.utils import timezone
from django.shortcuts import render
import datetime
import logging


def get_color_list():
    """ return a list of color variables, based on bootstrap theme definitions, to use in report templates """
    return ['theme.primary', 'theme.success', 'theme.secondary', 'theme.info', 'theme.warning',
            'theme.danger', 'theme.dark', 'theme.light']


def get_timestamps(now=None):
    """ return a tuple of time stamps; from a point in time (now) for the past day, week, month, and year """
    if not now:
        now = timezone.now()
    last_day = now - datetime.timedelta(days=1)
    last_week = now - datetime.timedelta(days=7)
    last_month = now - datetime.timedelta(days=365.2425 / 12)
    last_year = now - datetime.timedelta(days=365.2425)
    return last_day, last_week, last_month, last_year


def get_month_labels_and_timestamps(month_range, now=None):
    """ """
    month_label_list = list()
    month_ts_list = list()
    if not now:
        now = timezone.now()
    for i in month_range:
        end = now - datetime.timedelta(i * 365.2425 / 12)
        month_label_list.append(end.strftime('%B'))
        month_ts_list.append(end)
    return month_label_list, month_ts_list


def get_dated_data(queryset, ts_lookup):
    """
    return queryset of results filtered by the past day, week, month, and year

    Args:
        queryset: django queryset used in gathering day, week, month, year lookups
        ts_lookup: timestamp and expression to use in filter ex. (created_at__gte)

    Returns:
        tuple of querysets filtered by the past day, week, month, and year
    """
    last_day, last_week, last_month, last_year = get_timestamps()
    data_day = queryset.filter(**{ts_lookup: last_day})
    data_week = queryset.filter(**{ts_lookup: last_week})
    data_month = queryset.filter(**{ts_lookup: last_month})
    data_year = queryset.filter(**{ts_lookup: last_year})
    return data_day, data_week, data_month, data_year


def build_progress_chart(dataset_list):
    """
    process a list of dataset and return data required to plot an annual progress chart

    Args:
        dataset_list - (list of dictionaries) set of data to display; list of dictionaries containing the following:
                       title     - title to display for dataset
                       queryset  - queryset to use in counts
                       dt_field  - datetime field in model

                        example:
                            {title='Owners', queryset=Owner.objects.all(), dt_field='created_at'}

    Returns:
        tuple containing:
            list of month labels
            list of month timestamps
            list of dictionaries containing data needed to plot chart
    """
    now = timezone.now()
    month_range = range(11, -1, -1)
    return_dataset_list = list()
    color_list = get_color_list()
    month_labels, month_timestamps = get_month_labels_and_timestamps(month_range, now)

    color = 0
    for dataset in dataset_list:
        queryset_field_lte = dataset.get('dt_field') + '__lte'

        annual_monthly_counts = list()
        for i in month_range:
            end = now - datetime.timedelta(i * 365.2425 / 12)
            annual_monthly_counts.append(dataset.get('queryset').filter(**{queryset_field_lte: end}).count())

        return_dataset_list.append(
            dict(title=dataset.get('title'),
                 url=dataset.get('list_view'),
                 dt_field=dataset.get('dt_field'),
                 data=annual_monthly_counts,
                 color=color_list[color],
                 list_view=dataset.get('list_view'),
                 icon=dataset.get('icon'),
                 )
        )

        if color >= len(color_list) - 1:
            color = 0
        color += 1
    return month_labels, month_timestamps, return_dataset_list


class AnnualStatView(View):
    """
    Description:
        Tallies the number of entries added over the past year. Included are counts of entries sectioned by
        past day, week, month and year.

    Parameters:
        title         - title displayed on web page
        subtitle      - subtitle displayed on web page
        template_name - template to use in rendering
        dataset_list  - set of data to display; list of dictionaries containing the following:
                            title     - title to display for dataset
                            queryset  - queryset to use in counts
                            dt_field  - datetime field in model
                            icon      - fontawesome icon to display for dataset
                            list_view - list view of data (used in links)

                        example:
                            {title='Owners', queryset=Owner.objects.all(), dt_field='created_at',
                             icon='fas fa-users', list_view='/hostmgr/list_owners'), }
    """
    title = 'Annual Statistics Report'
    sub_title = None
    template_name = 'handyhelpers/report/annual_stats.html'
    dataset_list = list()

    def get(self, request):
        context = dict()
        context['title'] = self.title
        context['sub_title'] = self.sub_title
        context['dataset_list'] = []
        last_day, last_week, last_month, last_year = get_timestamps()

        for dataset in self.dataset_list:
            data_day, data_week, data_month, data_year = get_dated_data(
                dataset.get('queryset'),
                dataset.get('dt_field') + '__gte',
            )

            context['dataset_list'].append(
                dict(title=dataset.get('title'),
                     icon=dataset.get('icon'),
                     url=dataset.get('list_view'),
                     total=dataset.get('queryset').count(),
                     day_count=data_day.count(),
                     day_date=last_day,
                     week_count=data_week.count(),
                     week_date=last_week,
                     month_count=data_month.count(),
                     month_date=last_month,
                     year_count=data_year.count(),
                     year_date=last_year,
                     ),
            )
        return render(request, self.template_name, context)


class AnnualTrendView(View):
    """
    Description:
        Tallies the number of elements processed over the past year. Included are counts of elements processed in the
        past day, week, month and year. Also includes counts of elements processed by month for the past year.

    Parameters:
        title         - title displayed on web page
        subtitle      - subtitle displayed on web page
        template_name - template to use in rendering
        dataset_list  - set of data to display; list of dictionaries containing the following:
                            title     - title to display for dataset
                            queryset  - queryset to use in counts
                            dt_field  - datetime field in model

                        example:
                        {title='Owners', queryset=Owner.objects.all(), dt_field='created_at'}

    """
    title = 'Annual Trend Report'
    sub_title = 'data added over the past year'
    template_name = 'handyhelpers/report/annual_trends.html'
    dataset_list = list()

    def get(self, request):
        context = dict()
        context['title'] = self.title
        context['sub_title'] = self.sub_title
        context['dataset_list'] = list()
        now = timezone.now()
        month_range = range(0, 13)

        color_list = get_color_list()
        context['last_day'], context['last_week'], context['last_month'], context['last_year'] = get_timestamps()
        context['month_labels'], context['month_timestamps'] = get_month_labels_and_timestamps(month_range, now)

        color = 0
        for dataset in self.dataset_list:
            annual_data = []
            data_day, data_week, data_month, data_year = get_dated_data(
                dataset.get('queryset'),
                dataset.get('dt_field') + '__gte',
            )

            for months_ago in month_range:
                ts = now - datetime.timedelta(months_ago * 365.2425 / 12)
                try:
                    annual_data.append(len(
                        [i for i in data_year if getattr(i, dataset.get('dt_field')).month == ts.month and
                         getattr(i, dataset.get('dt_field')).year == ts.year]))
                except Exception as err:
                    logging.error(err)
                    annual_data.append(0)

            context['dataset_list'].append(
                dict(title=dataset.get('title'),
                     list_view=dataset.get('list_view'),
                     dt_field=dataset.get('dt_field'),
                     color=color_list[color],
                     day=data_day.count(),
                     week=data_week.count(),
                     month=data_month.count(),
                     year=data_year.count(),
                     annual=annual_data,
                     ),
            )
            color += 1
            if color > len(color_list):
                color = 0
        return render(request, self.template_name, context)


class AnnualProgressView(View):
    """
    Description:
        Show the current number of elements per dataset and chart showing counts of data added per month over the
        past year per dataset.

    Parameters:
        title         - title displayed on web page
        subtitle      - subtitle displayed on web page
        template_name - template to use in rendering
        dataset_list  - set of data to display; list of dictionaries containing the following:
                            title     - title to display for dataset
                            queryset  - queryset to use in counts
                            dt_field  - datetime field in model

                        example:
                        {title='Owners', queryset=Owner.objects.all(), dt_field='created_at'}

    """
    title = 'Annual Progress Report'
    sub_title = 'cumulative data added over the past year'
    template_name = 'handyhelpers/report/annual_progress.html'
    dataset_list = list()

    def get(self, request):
        context = dict()
        context['title'] = self.title
        context['sub_title'] = self.sub_title
        context['month_labels'], context['month_timestamps'], context['dataset_list'] = \
            build_progress_chart(self.dataset_list)
        return render(request, self.template_name, context=context)
