from django.db.models import QuerySet
import csv

from django.db.models.options import Options
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from shopapp.common import common_read_csv_file
from shopapp.forms import CSVImportForm


class ImportCsvMixin:
    """ Import csv file to database """
    def import_csv(self, request: HttpRequest) -> HttpResponse:
        meta: Options = self.model._meta
        # print("META", meta)
        if request.method == "GET":

            form = CSVImportForm()
            context = {
                "form": form
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)

        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)

        file = form.files["csv_file"].file
        encoding = request.encoding
        current_model = meta.model

        items = common_read_csv_file(
            file=file,
            encoding=encoding,
            model=current_model
        )

        current_model.save_csv(current_model, items)
        return redirect("..")


class ExportAsCSVMixin:
    def export_csv(self, request: HttpRequest, queryset: QuerySet):
        meta: Options = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response["Content-Desposition"] = f"attachment; filename={meta}-export.csv"

        csv_writer = csv.writer(response)
        csv_writer.writerow(field_names)
        for obj in queryset:
            csv_writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_csv.short_description = "Export as CSV"
