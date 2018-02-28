import csv
from django.http import HttpResponse
from django.views.generic import (View)


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

    def dispatch(self, request, *args, **kwargs):
        self.queryset = self.filter_by_query_params()
        return super(FilterByQueryParamsMixin, self).dispatch(request, *args, **kwargs)

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
            for field, val in self.request.GET.dict().iteritems():
                if field.split("__")[0] not in [i.name for i in model._meta.fields]:
                    continue
                if val is not None:
                    if val == 'None':
                        val = None
                    filter_dict[field] = val
            return self.queryset.filter(**filter_dict)
