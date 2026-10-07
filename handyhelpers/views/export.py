"""CSV and optional XLSX exports."""

import csv
from datetime import date, datetime
from io import BytesIO
from numbers import Number
from pathlib import Path

from django.http import HttpResponse
from django.views.generic import View

from handyhelpers.mixins.view_mixins import FilterByQueryParamsMixin
from handyhelpers.utils import optional_import


def safe_csv_value(value):
    text = "" if value is None else str(value)
    if not isinstance(value, Number) and text.lstrip().startswith(
        ("=", "+", "-", "@", "\t", "\r", "\n")
    ):
        text = "'" + text
    return text


class CsvExportView(FilterByQueryParamsMixin, View):
    filename = None

    def get(self, request, *args, **kwargs):
        queryset = self.filter_by_query_params()
        filename = Path(self.filename or queryset.model._meta.model_name).stem + ".csv"
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        fields = [field.name for field in queryset.model._meta.fields]
        writer = csv.writer(response)
        writer.writerow(fields)
        for row in queryset.iterator():
            writer.writerow([safe_csv_value(getattr(row, name)) for name in fields])
        return response


class ExcelExportView(FilterByQueryParamsMixin, View):
    """Export modern .xlsx files; requires django-handyhelpers[excel]."""

    filename = None

    def get(self, request, *args, **kwargs):
        openpyxl = optional_import("openpyxl", "excel")
        queryset = self.filter_by_query_params()
        workbook = openpyxl.Workbook(write_only=True)
        sheet = workbook.create_sheet(queryset.model._meta.model_name[:31])
        fields = [field.name for field in queryset.model._meta.fields]
        sheet.append(fields)
        for row in queryset.values_list(*fields).iterator():
            cells = []
            for value in row:
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif value is not None and not isinstance(value, (str, int, float, bool, date)):
                    value = str(value)
                cell = openpyxl.cell.WriteOnlyCell(sheet, value=value)
                if isinstance(value, str):
                    cell.data_type = "s"
                cells.append(cell)
            sheet.append(cells)
        output = BytesIO()
        workbook.save(output)
        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        filename = Path(self.filename or queryset.model._meta.model_name).stem + ".xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
