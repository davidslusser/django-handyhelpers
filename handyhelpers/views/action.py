"""Apply and clear conventional list filters using safely encoded redirects."""

from django.shortcuts import redirect
from django.views import View

from handyhelpers.utils import safe_return_url, update_query


class FilterListView(View):
    def post(self, request, *args, **kwargs):
        parameters = {
            key: request.POST.getlist(key)
            for key in request.POST
            if key != "csrfmiddlewaretoken" and request.POST.get(key)
        }
        return redirect(update_query(safe_return_url(request), parameters, replace=True))


class ShowAllListView(View):
    def get(self, request, *args, **kwargs):
        return redirect(update_query(safe_return_url(request), {}, replace=True))
