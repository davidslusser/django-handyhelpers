from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.template import loader
from django.views.generic import DetailView, View
from handyhelpers.views.gui import HandyHelperListView, HandyHelperIndexView
from handyhelpers.mixins.view_mixins import HtmxViewMixin
from handyhelpers.views.htmx import BuildModelSidebarNav, BuildBootstrapModalView


class CalendarView(View):
    template_name = "web/test/calendar.html"
    queryset = None
    title_field = None
    date_field = None
    url = None 
    modal_link = None
    color_field = None

    def parse_data():
        # convert queryset to a data dict to normalize field names of Event
        pass

    def get(self, request, *args, **kwargs):
        context = {}
        # context = {"queryset": Event.objects.all(),
        #            "group_list": TechGroup.objects.all()}
        return render(request, self.template_name, context)
