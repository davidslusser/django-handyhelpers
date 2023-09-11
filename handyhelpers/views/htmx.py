from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import View


class GenericHtmxView(View):
    """ Generic view for handling HTMX requests; intended to be used with snippets/partials.
    
    context       - context dictionary containing data to be rendered in template
    template_name - template used when rendering page; defaults to: handyhelpers/generic/generic_list.html
    """
    template_name = None
    context = {}
    
    def get(self, request, *args, **kwargs):
        if not self.request.headers.get("Hx-Request", None):
            return HttpResponse("Invalid request", status=400)  
        return render(request, self.template_name, self.context)


class BuildBootstrapModalView(GenericHtmxView):
    """ Generic view used to build a Boostrap 5 modal via HTMX.
    
    class parameters:
        template_name       - template used to render modal; defaults to "handyhelpers/htmx/bs5/modal_swap.htm"
        modal_size          - size of the modal; defaults to "modal-md"
        modal_title         - title used in modal header
        modal_subtitle      - subtitle used in modal header
        modal_body          - contents of modal body
        modal_button_close  - text to use on close button; defaults to "Close"
        modal_button_submit - text to use on submit button; defaults to "Submit"
    """
    template_name = "handyhelpers/htmx/bs5/generic_modal_swap.htm"
    modal_size = "modal-md"
    modal_title = None
    modal_subtitle = None
    modal_body = None
    modal_button_close = "Close"
    modal_button_submit = "Submit"
    data = {}
    extra_data = {}

    def get(self, request, *args, **kwargs):
        if not self.request.headers.get("Hx-Request", None):
            return HttpResponse('Invalid request', status=400)  
        self.context = {
            "modal_header": self.build_model_header(), 
            "modal_body": self.modal_body,
            "modal_size": self.modal_size,
            "modal_button_close": self.modal_button_close,
            "modal_button_submit": self.modal_button_submit,
            "data": self.data,
            "extra_data": self.extra_data
        }
        return super().get(request, *args, **kwargs)

    def build_model_header(self):
        context = {"modal_title": self.modal_title, "modal_subtitle": self.modal_subtitle}
        return loader.render_to_string("handyhelpers/htmx/bs5/modal_header.htm", context=context)


class AboutProjectModalView(BuildBootstrapModalView):
    """A htmx view used to show a Bootstrap 5 modal showing project specific information such as version. Data is pulled from the settings.py file.
    Example settings:
    
        PROJECT_NAME = "MyProject"
        PROJECT_DESCRIPTION = "A very informative description of my project"
        PROJECT_VERSION = "1.2.3"
        PROJECT_SOURCE = "https://github.com/myproject"
    """
    data = {
        "project_description": getattr(settings, "PROJECT_DESCRIPTION", None), 
        "project_name": getattr(settings, "PROJECT_NAME", None), 
        "project_source": getattr(settings, "PROJECT_SOURCE", None), 
        "project_version": getattr(settings, "PROJECT_VERSION", None), 
        }
    template_name = "handyhelpers/htmx/bs5/about_project_modal.htm"

    def get(self, request, *args, **kwargs):
        if getattr(settings, "HH_STARTTIME", None):
            self.data["uptime"] = f"{timezone.now() - settings.HH_STARTTIME}"
        return super().get(request, *args, **kwargs)
