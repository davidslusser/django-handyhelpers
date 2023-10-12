from django.conf import settings
from django.contrib import messages
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import View


class GenericHtmxView(View):
    """Generic view for handling HTMX requests; intended to be used with snippets/partials.

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
    """Generic view used to build a Boostrap 5 modal via HTMX.

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
    form_class = None
    modal_size = "modal-md"
    modal_title = None
    modal_subtitle = None
    modal_body = None
    modal_button_close = "Close"
    modal_button_submit = "Submit"
    show_messages = True
    data = {}
    extra_data = {}

    def get(self, request, *args, **kwargs):
        self.context = {
            "modal_title": self.modal_title,
            "modal_subtitle": self.modal_subtitle,
            "modal_body": self.modal_body,
            "modal_size": self.modal_size,
            "modal_button_close": self.modal_button_close,
            "modal_button_submit": self.modal_button_submit,
            "data": self.data,
            "extra_data": self.extra_data,
            "show_messages": self.show_messages,
        }
        if self.form_class:
            pre_fill_data = request.session.get(f"{self.form_class.__name__}", None)
            if pre_fill_data:
                form = self.form_class(initial=pre_fill_data["data"])
                form.cleaned_data = {}
                for k, v in pre_fill_data["errors"].items():
                    form.add_error(field=k, error=v)
                self.context["form"] = form
            else:
                self.context["form"] = self.form_class
        return super().get(request, *args, **kwargs)


class BoostrapModalFormCreateView(BuildBootstrapModalView):
    def post(self, request, *args, **kwargs):
        context = {}
        context["messages"] = []
        if not request.META.get("HTTP_HX_REQUEST"):
            return HttpResponse("Invalid request", status=400)
        form = self.form_class(self.request.POST or None)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            form.save_m2m()
            request.session[f"{form.__class__.__name__}"] = None
            context["messages"].append(
                {
                    "message_type": messages.INFO,
                    "message": f"{self.form_class.Meta.model._meta.model_name} {new} created!",
                    "extra_tags": "alert-success",
                }
            )
            return render(
                request, "handyhelpers/component/bs5/show_messages.htm", context=context
            )
        else:
            request.session[f"{form.__class__.__name__}"] = {
                "errors": form.errors,
                "data": form.data,
            }
            context["messages"].append(
                {
                    "message_type": messages.ERROR,
                    "message": f"Failed to create {self.form_class.Meta.model._meta.model_name}",
                    "extra_tags": "alert-danger",
                }
            )
            return render(
                request, "handyhelpers/component/bs5/show_messages.htm", context=context
            )


class AboutProjectModalView(BuildBootstrapModalView):
    """A htmx view used to show a Bootstrap 5 modal showing project specific information such as version. Data is pulled from the settings.py file.
    Example settings:

        PROJECT_NAME = "MyProject"
        PROJECT_DESCRIPTION = "A very informative description of my project"
        PROJECT_VERSION = "1.2.3"
        PROJECT_SOURCE = "https://github.com/myproject"
    """

    modal_button_submit = None
    modal_title = f"""About {getattr(settings, "PROJECT_NAME", None)}"""
    data = {
        "project_description": getattr(settings, "PROJECT_DESCRIPTION", None),
        "project_name": getattr(settings, "PROJECT_NAME", None),
        "project_source": getattr(settings, "PROJECT_SOURCE", None),
        "project_version": getattr(settings, "PROJECT_VERSION", None),
    }

    def get(self, request, *args, **kwargs):
        if getattr(settings, "HH_STARTTIME", None):
            context = {}
            self.data["uptime"] = f"{timezone.now() - settings.HH_STARTTIME}"
            context["data"] = self.data
            self.modal_body = loader.render_to_string(
                "handyhelpers/htmx/bs5/about_project_modal_body.htm", context=context
            )
        return super().get(request, *args, **kwargs)
