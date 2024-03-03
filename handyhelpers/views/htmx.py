from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import View
from handyhelpers.mixins.view_mixins import HtmxViewMixin


class BuildBootstrapModalView(HtmxViewMixin, View):
    """Generic view used to build a Boostrap 5 modal via htmx.

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
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        context = {
            "modal_title": self.modal_title,
            "modal_subtitle": self.modal_subtitle,
            "modal_body": self.modal_body,
            "modal_size": self.modal_size,
            "modal_button_close": self.modal_button_close,
            "modal_button_submit": self.modal_button_submit,
            "data": self.data,
            "extra_data": self.extra_data,
        }
        return render(request, self.template_name, context)


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


class HtmxSidebarItems(HtmxViewMixin, View):
    """View to process a htmx request and render a partial template intended to be used on a sidebar navigation.

    template_name - template used when rendering partial; defaults to: handyhelpers/htmx/bs5/sidebar_items.htm
    queryset      - queryset containing data to be rendered on the partial

    Usage Example:
        class GetSomeData(HtmxSidebarItems):
            queryset = MyModel.objects.all()
    """

    template_name = "handyhelpers/htmx/bs5/sidebar_menu_sub_items.htm"
    queryset = None

    def get(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        if self.queryset is not None:
            self.queryset._result_cache = None
        self.context = dict(
            queryset=self.queryset,
            args=self.args,
            kwargs=self.kwargs,
        )
        return render(request, self.template_name, self.context)



class BuildModelSidebarNav(HtmxViewMixin, View):
    """Dynamically build a sidebar navigation menu where items included are sourced from application models.
    This is intended handyhelpers_with_sidebar.htm or similar template.

    Class Parameters:
        template_name  - template used when rendering page; defaults to:
                         handyhelpers/htmx/bs5/navigation/build_sidebar.htm
        menu_item_list - list of dictionaries containing querysets (required) and icons (optional) to use in side menu

    Usage Example:

        class BuildSidebar(BuildSidebarNav):
            menu_item_list = [
                {"queryset": MyModelOne.objects.filter(date_time__gte=timezone.now()),
                "icon": '<i class="fa-solid fa-calendar-day"></i>',
                },
                {"queryset": MyModelOne.objects.filter(enabled=True),
                "icon": '<i class="fa-solid fa-people-group"></i>',
                "htmx_link": False,
                "list_all_url": "list_mymodelones",
                },
            ]
    """

    template_name = "handyhelpers/htmx/bs5/navigation/build_sidebar.htm"
    menu_item_list = []

    def get(self, request):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        for item in self.menu_item_list:
            queryset = item["queryset"]
            if queryset is not None:
                queryset._result_cache = None
            item["model_name"] = queryset.model._meta.verbose_name_plural
            item["target_id"] = queryset.model._meta.verbose_name_plural.replace(
                " ", "_"
            )
            item["link"] = hasattr(queryset.model, "get_absolute_url")
            if item.get("htmx_link", True) and not item.get("htmx_target", None):
                item["htmx_target"] = "body_main"
        context = dict(
            menu_item_list=self.menu_item_list,
        )
        return render(request, self.template_name, context)
