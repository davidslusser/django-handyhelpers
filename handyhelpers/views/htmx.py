from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, reverse
from django.utils import timezone
from django.views.generic import DetailView, View
from handyhelpers.mixins.view_mixins import FilterByQueryParamsMixin, HtmxViewMixin
from handyhelpers.views.gui import HandyHelperIndexView


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


class ModelDetailBootstrapModalView(BuildBootstrapModalView):
    modal_button_submit = None
    modal_template = None
    model = None

    def get(self, request, *args, **kwargs):
        context = {}
        context["object"] = self.model.objects.get(pk=kwargs["pk"])
        if self.modal_title == None:
            self.modal_title = f"{self.model._meta.object_name} Details"
        if self.modal_subtitle == None:
            self.modal_subtitle = context["object"]
        self.modal_body = loader.render_to_string(self.modal_template, context=context)
        return super().get(request, *args, **kwargs)


class HtmxPostForm(HtmxViewMixin, View):

    form = None
    template_name = "handyhelpers/htmx/bs5/form/form_wrapper.htm"

    def post(self, request, *args, **kwargs):

        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        context = {}
        form = self.form(request.POST)
        if form.is_valid():
            form.save()
            context["success"] = True
            context["form"] = self.form()
        else:
            context["form"] = form
        return render(request, self.template_name, context)


class CreateModelModalView(BuildBootstrapModalView):
    """ """

    modal_button_submit = "Create"
    modal_title = None
    form = None
    form_display = "bs5"

    def get(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        if not self.form:
            return HttpResponse("Invalid request", status=400)

        form_errors = request.session.get(f"{self.form.__name__}__errors")
        if self.form and form_errors:
            data = request.session.get(f"{self.form.__name__}__data")
            form = self.form()
            form.data = data
            for field, error_message in form_errors.items():
                try:
                    form.add_error(field, error_message)
                except:
                    pass
        else:
            form = self.form()

        context = {
            "modal_title": (
                self.modal_title
                if self.modal_title
                else f"Create {self.form.Meta.model._meta.object_name}"
            ),
            "modal_subtitle": self.modal_subtitle,
            "modal_body": self.modal_body,
            "modal_size": self.modal_size,
            "modal_button_close": self.modal_button_close,
            "modal_button_submit": self.modal_button_submit,
            "data": self.data,
            "extra_data": self.extra_data,
            "form": form,
            "form_display": self.form_display,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            obj = form.save()
            response = HttpResponse(status=204)
            response["X-Toast-Message"] = (
                f"""{obj._meta.object_name} '{obj}' created!"""
            )
            del request.session[f"{self.form.__name__}__errors"]
            del request.session[f"{self.form.__name__}__data"]
            return response
        else:
            form_error_dict = {}
            for k, v in form.errors.as_data().items():
                form_error_dict[k] = str(v[0].messages[0])
            request.session[f"{self.form.__name__}__errors"] = form_error_dict
            request.session[f"{self.form.__name__}__data"] = form.data
            response = HttpResponse(status=400)
            response["X-Toast-Message"] = (
                f"""<span class="text-danger">Failed to create new {self.form.Meta.model._meta.object_name}</span>"""
            )
            return response


class HtmxOptionView(HtmxViewMixin, View):
    template_name = None
    htmx_template_name = None
    context = {}

    def get(self, request):
        if self.is_htmx() and self.template_name:
            template_name = self.htmx_template_name
        else:
            template_name = self.template_name
        return render(request, template_name, self.context)


class HtmxOptionDetailView(HtmxViewMixin, DetailView):
    template_name = None
    htmx_template_name = None
    initialize_tables = None

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        if self.initialize_tables:
            response["X-Initialize-Tables"] = "initialize-tables"
        return response

    def get(self, request, *args, **kwargs):
        if self.is_htmx() and self.htmx_template_name:
            self.template_name = self.htmx_template_name
        return super().get(request, *args, **kwargs)


class HtmxOptionMultiView(HtmxViewMixin, View):
    title = None
    subtitle = None
    model = None
    template_name = None
    htmx_template_name = None
    htmx_card_template_name = None
    htmx_custom_template_name = None
    htmx_index_template_name = None
    htmx_list_template_name = None
    htmx_minimal_template_name = None
    htmx_table_template_name = None
    htmx_table_wrapper_template_name = "handyhelpers/htmx/bs5/table_wrapper.htm"
    context = {}
    queryset = None

    def get(self, request, **kwargs):
        template_name = None
        if self.queryset is not None:
            self.queryset._result_cache = None
        if self.is_htmx():
            display = kwargs.get("display", None)
            if display:
                if display == "card" and self.htmx_card_template_name:
                    template_name = self.htmx_card_template_name
                elif display == "custom" and self.htmx_custom_template_name:
                    template_name = self.htmx_custom_template_name
                elif display == "index" and self.htmx_index_template_name:
                    template_name = self.htmx_index_template_name
                elif display == "list" and self.htmx_list_template_name:
                    template_name = self.htmx_list_template_name
                elif display == "minimal" and self.htmx_minimal_template_name:
                    template_name = self.htmx_minimal_template_name
                elif display == "table" and self.htmx_table_wrapper_template_name:
                    template_name = self.htmx_table_wrapper_template_name
                    self.context["table"] = self.htmx_table_template_name
                elif self.htmx_template_name:
                    template_name = self.htmx_template_name
            else:
                return HttpResponse("", content_type="text/plain")
        else:
            template_name = self.template_name
        if self.queryset:
            self.context["queryset"] = self.queryset
        elif self.model:
            self.context["queryset"] = self.model.objects.all()

        if self.title:
            self.context["title"] = self.title
        elif self.model:
            self.context["title"] = self.model._meta.verbose_name_plural.title()

        self.context["subtitle"] = self.subtitle
        return render(request, template_name, self.context)


class HtmxOptionMultiFilterView(FilterByQueryParamsMixin, HtmxViewMixin, View):
    context = {}
    default_display = "table"
    filter_form = None
    htmx_card_template_name = None
    htmx_card_wrapper_template_name = (
        "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/wrapper_card.htm"
    )
    htmx_list_template_name = None
    htmx_list_wrapper_template_name = (
        "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/wrapper_list.htm"
    )
    htmx_minimal_template_name = None
    htmx_minimal_wrapper_template_name = (
        "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/wrapper_minimal.htm"
    )
    htmx_table_template_name = None
    htmx_table_wrapper_template_name = (
        "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/wrapper_table.htm"
    )
    htmx_template_name = None
    model = None
    queryset = None
    subtitle = None
    template_name = "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/full.html"
    title = None

    def get(self, request, post_data={}, *args, **kwargs):
        page_description = request.GET.get("page_description", None)
        control_list = []
        display = kwargs.get("display", None)
        if not display:
            display = self.default_display
        root_url = reverse(
            f"{request.resolver_match.app_name}:{request.resolver_match.url_name}"
        ).replace("//", "/")
        query_params = request.GET
        template_name = None

        if post_data:
            query_string = ""
            url = f"""{root_url}?"""
            for key, value in post_data.items():
                if value:
                    url += f"{key}={value}&"
                    query_string += f"{key}={value}&"
        elif query_params:
            query_string = query_params.urlencode()
            url = f"{root_url}{display}?{query_string}"
        else:
            query_string = ""
            url = f"{root_url}{display}"

        if self.queryset is not None:
            self.queryset._result_cache = None
        if self.is_htmx():
            if display == "card" and self.htmx_card_wrapper_template_name:
                template_name = self.htmx_card_wrapper_template_name
                self.context["item_content"] = self.htmx_card_template_name
            elif display == "list" and self.htmx_list_wrapper_template_name:
                template_name = self.htmx_list_wrapper_template_name
                self.context["item_content"] = self.htmx_list_template_name
            elif display == "minimal" and self.htmx_minimal_template_name:
                template_name = self.htmx_minimal_wrapper_template_name
                self.context["item_content"] = self.htmx_minimal_template_name
            elif display == "table" and self.htmx_table_wrapper_template_name:
                template_name = self.htmx_table_wrapper_template_name
                self.context["item_content"] = self.htmx_table_template_name
            elif self.htmx_template_name:
                template_name = self.htmx_template_name
        else:
            template_name = self.template_name

        # add display controls
        if self.htmx_card_template_name:
            control_list.append(
                {
                    "name": "card",
                    "icon": """<i class="fa-regular fa-square"></i>""",
                    "url": (
                        f"{root_url}card/?{query_string}"
                        if query_string
                        else f"{root_url}card/"
                    ),
                }
            )
        if self.htmx_list_template_name:
            control_list.append(
                {
                    "name": "list",
                    "icon": """<i class="fa-solid fa-list-ul"></i>""",
                    "url": (
                        f"{root_url}list/?{query_string}"
                        if query_string
                        else f"{root_url}list/"
                    ),
                }
            )
        if self.htmx_minimal_template_name:
            control_list.append(
                {
                    "name": "minimal",
                    "icon": """<i class="fa-solid fa-compress"></i>""",
                    "url": (
                        f"{root_url}minimal/?{query_string}"
                        if query_string
                        else f"{root_url}minimal/"
                    ),
                }
            )
        if self.htmx_table_template_name:
            control_list.append(
                {
                    "name": "table",
                    "icon": """<i class="fa-solid fa-table"></i>""",
                    "url": (
                        f"{root_url}table/?{query_string}"
                        if query_string
                        else f"{root_url}table/"
                    ),
                }
            )

        if self.queryset == None and self.model:
            self.queryset = self.model.objects.all()
        if post_data:
            self.queryset = self.queryset.filter(**post_data)
        elif query_params:
            self.queryset = self.filter_by_query_params()
        self.context["queryset"] = self.queryset
        self.context["title"] = self.title
        self.context["control_list"] = control_list
        self.context["display"] = display
        self.context["filter_form"] = self.filter_form
        self.context["htmx_template_name"] = template_name
        self.context["page_description"] = page_description
        self.context["query_string"] = query_string
        self.context["root_url"] = root_url
        self.context["subtitle"] = self.subtitle
        self.context["url"] = url

        response = render(request, template_name, self.context)
        if self.is_htmx():
            response["X-Initialize-Tables"] = "initialize-tables"
        return response

    def post(self, request, *args, **kwargs):
        """build filter string from form fields and call get method to update queryset"""
        form = self.filter_form(request.POST)
        if form.is_valid():
            post_data = {
                key: value for key, value in request.POST.dict().items() if value
            }
        return self.get(request, post_data, *args, **kwargs)


class HtmxItemizedView(HtmxViewMixin, HandyHelperIndexView):
    template_name = "handyhelpers/generic/bs5/generic_index.html"
    htmx_template_name = "handyhelpers/htmx/bs5/index.htm"

    def get(self, request, *args, **kwargs):
        if self.is_htmx() and self.htmx_template_name:
            self.template_name = self.htmx_template_name
        return super().get(request, *args, **kwargs)


class HtmxFilterModalView(BuildBootstrapModalView):
    """Render a modal containing a filter form"""

    form = None
    form_display = "bs5"
    modal_button_submit = "Filter"
    modal_title = "Filter"
    template_name = (
        "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/filter_form_modal_swap.htm"
    )

    def get(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        if not self.form:
            return HttpResponse("Invalid request", status=400)

        list_display = request.GET.get("display", None)

        context = {
            "data": self.data,
            "display": list_display,
            "extra_data": self.extra_data,
            "form": self.form,
            "form_display": self.form_display,
            "modal_body": self.modal_body,
            "modal_button_close": self.modal_button_close,
            "modal_button_submit": self.modal_button_submit,
            "modal_size": self.modal_size,
            "modal_subtitle": self.modal_subtitle,
            "modal_title": self.modal_title,
        }
        return render(request, self.template_name, context)
