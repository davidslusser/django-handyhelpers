from django.shortcuts import render
from django.views.generic import (View, ListView)

# import HandyHelpers
from handyhelpers.views import CsvExportView

# import models
from models import Artist


class CatalogHomeView(View):
    """ show catalog home page """
    @staticmethod
    def get(request):
        template = "show_catalog_home.html"
        context = dict()
        return render(request, template, context)


class ArtistCsvView(CsvExportView):
    """ export all artists directly to a csv file """
    queryset = Artist.objects.all()
