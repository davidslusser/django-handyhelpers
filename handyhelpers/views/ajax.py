"""Reusable JSON-wrapped HTML response for conventional AJAX components."""

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View

from handyhelpers.utils import RequestStateMixin


class AjaxGetView(RequestStateMixin, View):
    template_name = None
    data = None

    def get(self, request, *args, **kwargs):
        if request.headers.get("X-Requested-With") != "XMLHttpRequest":
            return JsonResponse({"detail": "Invalid request"}, status=400)
        if "client_response" not in request.GET:
            return JsonResponse({"detail": "Invalid request inputs"}, status=400)
        return JsonResponse(
            {
                "server_response": render_to_string(
                    self.template_name, {"data": self.data}, request=request
                )
            }
        )
