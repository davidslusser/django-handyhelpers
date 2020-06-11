import datetime
import csv
import xlwt
from django.http import HttpResponse
from django.views.generic import View
from handyhelpers.mixins.view_mixins import FilterByQueryParamsMixin


class CsvExportView(FilterByQueryParamsMixin, View):
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

            queryset = self.filter_by_query_params()
            for row in queryset:
                writer.writerow({column: str(getattr(row, column)) for column in headers})
            return response
        except AttributeError:
            return HttpResponse(content_type='text/csv')


class ExcelExportView(FilterByQueryParamsMixin, View):
    """ dump a queryset to an Excel file """
    queryset = None
    filename = None

    def get(self, request):
        try:
            model = self.queryset.model
            if not self.filename:
                self.filename = "{}.xls".format(model._meta.model_name)
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.filename)

            wb = xlwt.Workbook(encoding='utf-8')
            ws = wb.add_sheet(model._meta.model_name)

            # Sheet header, first row
            row_num = 0

            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            columns = [field.name for field in model._meta.fields]

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            # Sheet body, remaining rows
            font_style = xlwt.XFStyle()

            queryset = self.filter_by_query_params()
            for row in queryset.values_list():
                row_num += 1
                for col_num in range(len(row)):
                    if type(row[col_num]) == datetime.datetime:
                        cell_data = str(row[col_num])
                    else:
                        cell_data = row[col_num]
                    ws.write(row_num, col_num, cell_data, font_style)
            wb.save(response)
            return response

        except AttributeError:
            return HttpResponse(content_type='application/ms-excel')
