"""
Description:
    Collection of handy generic views

"""

import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import (View)
from django.utils import timezone
import datetime
import logging


class SimpleView(View):
    """ super simple view for displaying a page with no queried data """
    template_name = None
    data = dict()

    def get(self, request):
        return render(request, self.template_name, self.data)


class CsvExportView(View):
    """ dump a queryset to a csv file """
    queryset = None
    filename = None

    def get(self, request):
        try:
            model = self.queryset.model
            if not self.filename:
                self.filename = "{}.csv".format(model._meta.model_name)
            response = HttpResponse(content_type='text/csv')
            cd = 'attachment; filename="{0}"'.format(self.filename)
            response['Content-Disposition'] = cd
            headers = [field.name for field in model._meta.fields]
            writer = csv.DictWriter(response, fieldnames=headers)
            writer.writeheader()
            for row in self.queryset:
                writer.writerow({column: str(getattr(row, column)) for column in headers})
            return response
        except AttributeError:
            return HttpResponse(content_type='text/csv')


class FilterByQueryParamsMixin:
    """ """
    request = None
    queryset = None
    page_description = None

    def filter_by_query_params(self):
            """
            Description:
                Filters a queryset by query_params in the URL

            Returns:
                filtered queryset
            """
            # pass a description to the view if included as a query parameter
            if not self.page_description and 'page_description' in self.request.GET.dict():
                self.page_description = self.request.GET.dict().get('page_description', None)

            # build a dictionary of valid model fields
            filter_dict = {}
            model = self.queryset.model
            for field, val in self.request.GET.dict().items():
                if field.split("__")[0] not in [i.name for i in model._meta.fields +
                                                                model._meta.many_to_many +
                                                                model._meta.related_objects
                                                ]:
                    continue
                if val is not None:
                    if val == 'None':
                        val = None
                    filter_dict[field] = val
            return self.queryset.filter(**filter_dict)


class AnnualTrendView(View):
    """
    Description:
        Tallies the number of elements added/removed over the past year. Included are counts of elements added and
        removed in the past day, week, month and year.
        Also includes counts of elements added and removed by month for the past year.
    """
    title = "Annual Trend Report"
    sub_title = None
    template_name = None
    added_queryset = None
    removed_queryset = None
    added_query_field = None
    removed_query_field = None

    def get(self, request):
        context = dict()
        context['title'] = self.title
        context['sub_title'] = self.sub_title
        last_day = timezone.now() - datetime.timedelta(days=1)
        last_week = timezone.now() - datetime.timedelta(days=7)
        last_month = timezone.now() - datetime.timedelta(days=365.2425 / 12)
        last_year = timezone.now() - datetime.timedelta(days=365.2425)

        added_query_field = self.added_query_field + "__gte"
        removed_query_field = self.removed_query_field + "__gte"

        added_day = self.added_queryset.filter(**{added_query_field: last_day})
        removed_day = self.removed_queryset.filter(**{removed_query_field: last_day})
        added_week = self.added_queryset.filter(**{added_query_field: last_week})
        removed_week = self.removed_queryset.filter(**{removed_query_field: last_week})
        added_month = self.added_queryset.filter(**{added_query_field: last_month})
        removed_month = self.removed_queryset.filter(**{removed_query_field: last_month})
        added_year = self.added_queryset.filter(**{added_query_field: last_year})
        removed_year = self.removed_queryset.filter(**{removed_query_field: last_year})

        context['month_labels'] = []
        context['added_per_month'] = []
        context['removed_per_month'] = []
        for i in range(0, 13):
            ts = timezone.now() - datetime.timedelta(i * 365.2425 / 12)
            context['month_labels'].append(ts.strftime("%B"))
            try:
                context['added_per_month'].append(len(
                    [i for i in added_year if getattr(i, self.added_query_field).month == ts.month and
                     getattr(i, self.added_query_field).year == ts.year]))
            except Exception as err:
                logging.error(err)
                context['added_per_month'].append(0)
            try:
                context['removed_per_month'].append(len(
                    [i for i in removed_year if getattr(i, self.removed_query_field).month == ts.month and
                     getattr(i, self.removed_query_field).year == ts.year]))
            except Exception as err:
                logging.error(err)
                context['removed_per_month'].append(0)

        context['added_day'] = added_day.count()
        context['removed_day'] = removed_day.count()
        context['added_week'] = added_week.count()
        context['removed_week'] = removed_week.count()
        context['added_month'] = added_month.count()
        context['removed_month'] = removed_month.count()
        context['added_year'] = added_year.count()
        context['removed_year'] = removed_year.count()
        return render(request, self.template_name, context)
