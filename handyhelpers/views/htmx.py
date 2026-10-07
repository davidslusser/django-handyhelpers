"""HTMX pages, partials, forms, and Bootstrap 5 modals."""

import json

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.views.generic import DetailView, View

from handyhelpers.mixins.view_mixins import FilterByQueryParamsMixin, HtmxViewMixin
from handyhelpers.utils import base_template_name, update_query
from handyhelpers.views.gui import HandyHelperIndexView


class BuildBootstrapModalView(HtmxViewMixin, View):
    template_name = "handyhelpers/htmx/bs5/generic_modal_swap.htm"
    modal_size = "modal-lg"
    modal_title = modal_subtitle = modal_body = None
    modal_button_close = "Close"
    modal_button_submit = "Submit"
    data = None
    extra_data = None

    def get_context_data(self, **kwargs):
        names = (
            "modal_title",
            "modal_subtitle",
            "modal_body",
            "modal_size",
            "modal_button_close",
            "modal_button_submit",
            "data",
            "extra_data",
        )
        return {**{name: getattr(self, name) for name in names}, **kwargs}

    def get(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        return render(request, self.template_name, self.get_context_data())


class AboutProjectModalView(BuildBootstrapModalView):
    modal_button_submit = None

    def get(self, request, *args, **kwargs):
        self.modal_title = f"About {getattr(settings, 'PROJECT_NAME', 'Project')}"
        self.data = {
            f"project_{name}": getattr(settings, f"PROJECT_{name.upper()}", "")
            for name in ("description", "name", "source", "version")
        }
        start = getattr(settings, "HH_STARTTIME", None)
        if start:
            self.data["uptime"] = str(timezone.now() - start)
        self.modal_body = render_to_string(
            "handyhelpers/htmx/bs5/about_project_modal_body.htm",
            {"data": self.data},
            request=request,
        )
        return super().get(request, *args, **kwargs)


class HtmxSidebarItems(HtmxViewMixin, View):
    template_name = "handyhelpers/htmx/bs5/navigation/sidebar_menu_sub_items.htm"
    queryset = None

    def get(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        return render(
            request,
            self.template_name,
            {
                "queryset": self.queryset.all() if self.queryset is not None else None,
                "args": args,
                "kwargs": kwargs,
            },
        )


class BuildModelSidebarNav(HtmxViewMixin, View):
    template_name = "handyhelpers/htmx/bs5/navigation/build_sidebar.htm"
    menu_item_list = ()

    def get(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        items = self._copy_config(self.menu_item_list)
        for item in items:
            queryset = item.get("queryset")
            if queryset is None:
                raise ImproperlyConfigured("Each sidebar item needs a queryset.")
            item["queryset"] = queryset.all()
            item["model_name"] = queryset.model._meta.verbose_name_plural
            item["target_id"] = queryset.model._meta.label_lower.replace(".", "_")
            item["link"] = hasattr(queryset.model, "get_absolute_url")
            item.setdefault("htmx_target", "body_main")
        return render(request, self.template_name, {"menu_item_list": items})


class ModelDetailBootstrapModalView(BuildBootstrapModalView):
    modal_button_submit = None
    modal_template = model = None

    def get(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        obj = get_object_or_404(self.model, pk=kwargs["pk"])
        self.modal_title = self.modal_title or f"{self.model._meta.object_name} Details"
        self.modal_subtitle = self.modal_subtitle or obj
        self.modal_body = render_to_string(self.modal_template, {"object": obj}, request=request)
        return super().get(request, *args, **kwargs)


class HtmxPostForm(HtmxViewMixin, View):
    form = None
    template_name = "handyhelpers/htmx/bs5/form/form_wrapper.htm"

    def post(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        form = self.form(request.POST, request.FILES)
        success = form.is_valid()
        if success:
            form.save()
        return render(
            request,
            self.template_name,
            {"form": form, "success": success},
            status=200 if success else 422,
        )


class HtmxFormPostSimple(HtmxPostForm):
    success_message = None

    def post(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        form = self.form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponse(
                self.success_message
                or getattr(form, "success_message", None)
                or "Request received, thanks!",
                status=201,
                content_type="text/plain",
            )
        return HttpResponse(form.errors.as_text(), status=400, content_type="text/plain")


class CreateModelModalView(BuildBootstrapModalView):
    modal_button_submit = "Create"
    form = None
    form_display = "bs5"

    def render_form(self, request, form, status=200):
        title = self.modal_title or f"Create {form._meta.model._meta.object_name}"
        return render(
            request,
            self.template_name,
            self.get_context_data(form=form, form_display=self.form_display, modal_title=title),
            status=status,
        )

    def get(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        if self.form is None:
            raise ImproperlyConfigured("Set form to a ModelForm class.")
        return self.render_form(request, self.form())

    def post(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        form = self.form(request.POST, request.FILES)
        if not form.is_valid():
            return self.render_form(request, form, status=422)
        obj = form.save()
        response = HttpResponse(status=204)
        response["HX-Trigger"] = json.dumps(
            {"handyhelpers:created": {"message": f"{obj._meta.object_name} '{obj}' created!"}}
        )
        return response


class HtmxOnlyView(HtmxViewMixin, View):
    htmx_template_name = None
    context = None

    def get(self, request, *args, **kwargs):
        if self.is_htmx() and self.htmx_template_name:
            return render(request, self.htmx_template_name, self.context or {})
        return HttpResponse(status=204)


class HtmxPartialView(HtmxOnlyView):
    pass


class HtmxOptionView(HtmxViewMixin, View):
    template_name = htmx_template_name = None
    base_template = None
    context = None

    def get(self, request, *args, **kwargs):
        name = (
            self.htmx_template_name
            if self.is_htmx() and self.htmx_template_name
            else self.template_name
        )
        return render(
            request,
            name,
            {"base_template": base_template_name(self.base_template), **(self.context or {})},
        )


class HtmxOptionDetailView(HtmxViewMixin, DetailView):
    htmx_template_name = None
    initialize_tables = False
    base_template = None

    def get_template_names(self):
        if self.is_htmx() and self.htmx_template_name:
            return [self.htmx_template_name]
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "base_template": base_template_name(self.base_template),
        }

    def render_to_response(self, context, **kwargs):
        response = super().render_to_response(context, **kwargs)
        if self.initialize_tables:
            response["X-Initialize-Tables"] = "initialize-tables"
        return response


class HtmxOptionMultiView(HtmxOptionView):
    title = subtitle = model = queryset = None
    htmx_card_template_name = htmx_custom_template_name = htmx_index_template_name = None
    htmx_list_template_name = htmx_minimal_template_name = htmx_table_template_name = None
    htmx_table_wrapper_template_name = "handyhelpers/htmx/bs5/table_wrapper.htm"

    def get(self, request, *args, **kwargs):
        context = dict(self.context or {})
        context.update(
            title=self.title
            or (self.model._meta.verbose_name_plural.title() if self.model else ""),
            subtitle=self.subtitle,
            base_template=base_template_name(self.base_template),
        )
        context["queryset"] = (
            self.queryset.all()
            if self.queryset is not None
            else (self.model._default_manager.all() if self.model else None)
        )
        template = self.template_name
        if self.is_htmx():
            display = kwargs.get("display") or request.GET.get("display")
            if display not in {"card", "custom", "index", "list", "minimal", "table"}:
                if not self.htmx_template_name:
                    return HttpResponse("Invalid display", status=400)
                template = self.htmx_template_name
            elif display == "table":
                template = self.htmx_table_wrapper_template_name
                context["table"] = self.htmx_table_template_name
            else:
                template = getattr(self, f"htmx_{display}_template_name") or self.htmx_template_name
        if not template:
            return HttpResponse("Unconfigured display", status=400)
        return render(request, template, context)


class HtmxOptionMultiFilterView(FilterByQueryParamsMixin, HtmxViewMixin, View):
    context = None
    base_template = None
    default_display = "table"
    filter_form = None
    title = subtitle = model = None
    template_name = "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/full.html"
    htmx_template_name = None
    htmx_card_template_name = htmx_list_template_name = htmx_minimal_template_name = (
        htmx_table_template_name
    ) = None
    htmx_card_wrapper_template_name = (
        "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/wrapper_card.htm"
    )
    htmx_list_wrapper_template_name = (
        "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/wrapper_list.htm"
    )
    htmx_minimal_wrapper_template_name = (
        "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/wrapper_minimal.htm"
    )
    htmx_table_wrapper_template_name = (
        "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/wrapper_table.htm"
    )

    def get_display_url(self, display):
        match = self.request.resolver_match
        if match is None:
            return update_query(self.request.path, {"display": display})
        try:
            return reverse(match.view_name, kwargs={**match.kwargs, "display": display})
        except NoReverseMatch:
            return update_query(reverse(match.view_name, kwargs=match.kwargs), {"display": display})

    def get(self, request, *args, filter_data=None, **kwargs):
        display = kwargs.get("display") or request.GET.get("display") or self.default_display
        if display not in {"card", "list", "minimal", "table"}:
            return HttpResponse("Invalid display", status=400)
        item_content = getattr(self, f"htmx_{display}_template_name")
        partial = (
            getattr(self, f"htmx_{display}_wrapper_template_name")
            if item_content
            else self.htmx_template_name
        )
        if not partial:
            return HttpResponse("Unconfigured display", status=400)
        queryset = self.filter_by_query_params(filter_data)
        params = request.GET.dict() if filter_data is None else filter_data
        params = {key: value for key, value in params.items() if key not in {"display", "page"}}
        controls = [
            {
                "name": name,
                "icon": f'<i class="fa-solid fa-{icon}"></i>',
                "url": update_query(self.get_display_url(name), params),
            }
            for name, icon in [
                ("card", "square"),
                ("list", "list-ul"),
                ("minimal", "compress"),
                ("table", "table"),
            ]
            if getattr(self, f"htmx_{name}_template_name")
        ]
        context = {
            **(self.context or {}),
            "queryset": queryset,
            "item_content": item_content,
            "base_template": base_template_name(self.base_template),
            "title": self.title,
            "subtitle": self.subtitle,
            "control_list": controls,
            "display": display,
            "filter_form": self.filter_form,
            "page_description": self.page_description,
            "htmx_template_name": partial,
            "root_url": self.get_display_url(display),
            "url": update_query(self.get_display_url(display), params),
            "query_string": update_query("", params).lstrip("?"),
        }
        response = render(request, partial if self.is_htmx() else self.template_name, context)
        response["X-Initialize-Tables"] = "initialize-tables"
        return response

    def post(self, request, *args, **kwargs):
        if self.filter_form is None:
            raise ImproperlyConfigured("Set filter_form to a form class.")
        form = self.filter_form(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponse(form.errors.as_text(), status=400, content_type="text/plain")
        return self.get(
            request,
            *args,
            filter_data={
                key: value for key, value in form.cleaned_data.items() if value not in (None, "")
            },
            **kwargs,
        )


class HtmxItemizedView(HtmxViewMixin, HandyHelperIndexView):
    template_name = "handyhelpers/htmx/bs5/full/itemized.html"
    htmx_template_name = "handyhelpers/htmx/bs5/partial/itemized.htm"

    def get(self, request, *args, **kwargs):
        if self.is_htmx():
            self.template_name = self.htmx_template_name
        return super().get(request, *args, **kwargs)


class HtmxFilterModalView(BuildBootstrapModalView):
    form = None
    form_display = "bs5"
    modal_button_submit = modal_title = "Filter"
    template_name = "handyhelpers/htmx/bs5/htmx_option_multi_filter_view/filter_form_modal_swap.htm"

    def get(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        form = self.form(initial=request.GET.dict())
        context = self.get_context_data(
            form=form,
            form_display=self.form_display,
            display=request.GET.get(
                "display", self.default_display if hasattr(self, "default_display") else "table"
            ),
        )
        return render(request, self.template_name, context)


class HtmxActionView(HtmxViewMixin, View):
    success_toast = "success!"
    fail_toast = "failed!"

    def action(self):
        """Override; return None for success and a non-None value for failure."""

    def post(self, request, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse("Invalid request", status=400)
        response = HttpResponse(status=204)
        response["X-Toast-Message"] = (
            self.fail_toast if self.action() is not None else self.success_toast
        )
        return response


class HtmxLoadModalView(HtmxViewMixin, View):
    default_modal_template = "handyhelpers/htmx/custom/modals/blank.htm"
    modal_template_map = None

    def get(self, request, modal_name, *args, **kwargs):
        if not self.is_htmx():
            return HttpResponse(status=204)
        return render(
            request, (self.modal_template_map or {}).get(modal_name, self.default_modal_template)
        )
