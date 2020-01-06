import csv
from django.http import HttpResponse
from django.views.generic import View


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
