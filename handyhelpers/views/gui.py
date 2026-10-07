"""Reusable Bootstrap 5 pages and conventional list views."""

from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import ListView, View

from handyhelpers.mixins.view_mixins import FilterByQueryParamsMixin
from handyhelpers.utils import RequestStateMixin, base_template_name


class HandyHelperGenericBaseView(RequestStateMixin, View):
    base_template = None

    def get_context_data(self, **kwargs):
        return {
            "base_template": base_template_name(self.base_template),
            "args": self.args,
            "kwargs": self.kwargs,
            **kwargs,
        }


class HandyHelperGenericBaseItemizedView(HandyHelperGenericBaseView):
    title = None
    subtitle = None
    item_list = None
    protected_item_list = None
    protected_group_name = None

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            title=self.title,
            subtitle=self.subtitle,
            item_list=self.item_list,
            protected_item_list=self.protected_item_list,
            protected_group_name=self.protected_group_name,
            **kwargs,
        )


class HandyHelperIndexView(HandyHelperGenericBaseItemizedView):
    template_name = "handyhelpers/generic/bs5/generic_index.html"
    htmx_template_name = None

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            self.get_context_data(htmx_template_name=self.htmx_template_name),
        )


class HandyHelperActionView(HandyHelperGenericBaseItemizedView):
    template_name = "handyhelpers/generic/bs5/generic_action.html"
    form_list = None

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(form_list=self.form_list))


class HandyHelperAboutView(HandyHelperGenericBaseView):
    template_name = "handyhelpers/generic/bs5/generic_about.html"
    title = "About"
    subtitle = version = details = source = contact = None
    links = ()

    def get(self, request, *args, **kwargs):
        context = {
            name: getattr(self, name)
            for name in ("title", "subtitle", "version", "details", "source", "contact", "links")
        }
        return render(request, self.template_name, self.get_context_data(**context))


class HandyHelperSingletonView(HandyHelperGenericBaseView):
    template_name = None
    model = None

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(object=self.model.load()))


class HandyHelperGenericBaseListView(FilterByQueryParamsMixin, ListView):
    base_template = None
    template_name = "handyhelpers/generic/bs5/generic_list.html"
    title = table = modals = add_static = add_template = None
    extra_controls = None

    def get_queryset(self):
        return self.filter_by_query_params()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            base_template=base_template_name(self.base_template),
            queryset=self.object_list,
            title=self.title,
            subtitle=self.page_description,
            table=self.table,
            modals=self.modals,
            add_static=self.add_static,
            add_template=self.add_template,
            extra_controls=self.extra_controls,
            args=self.args,
            kwargs=self.kwargs,
        )
        return context


class HandyHelperListView(HandyHelperGenericBaseListView):
    """List records with optional create/filter modal forms.

    Set ``create_form_obj`` and/or ``filter_form_obj`` to a form class. Configure
    either modal with the corresponding ``*_form_*`` attributes below.
    Group visibility is presentation only; authorize the action endpoint separately.
    """

    create_form_obj = create_form_url = create_form_title = create_form_modal_name = None
    create_form_id = create_form_modal_size = create_form_modal_backdrop = None
    create_form_link_title = create_form_tool_tip = create_form_autocomplete = None
    create_form_modal_scrollable = False
    filter_form_obj = filter_form_title = filter_form_modal_name = None
    filter_form_id = filter_form_modal_size = filter_form_modal_backdrop = None
    filter_form_link_title = filter_form_tool_tip = filter_form_autocomplete = None
    filter_form_modal_scrollable = False
    filter_form_url = None
    filter_form_undo = True
    allow_create_groups = None

    def get_context_data(self, **kwargs):
        from django.urls import reverse

        context = super().get_context_data(**kwargs)
        context["allow_create_groups"] = self.allow_create_groups
        for kind, action in [("create", "Add"), ("filter", "Filter")]:
            form_class = getattr(self, f"{kind}_form_obj")
            if form_class is None:
                continue
            initial = self.request.GET.dict() if kind == "filter" else None
            form = form_class(initial=initial)
            data = {"form": form, "action": action}
            for attribute in (
                "form_id",
                "title",
                "modal_name",
                "modal_size",
                "modal_backdrop",
                "modal_scrollable",
                "link_title",
                "tool_tip",
                "autocomplete",
            ):
                name = attribute if attribute == "form_id" else "form_" + attribute
                data[attribute] = getattr(self, f"{kind}_{name}", None)
            data["form_id"] = getattr(self, f"{kind}_form_id")
            data["modal_name"] = data["modal_name"] or kind
            data["action_url"] = getattr(self, f"{kind}_form_url") or (
                reverse("handyhelpers:filter_list_view") if kind == "filter" else ""
            )
            if kind == "filter":
                data["undo"] = self.filter_form_undo
            context[f"{kind}_form"] = data
        return context


class HandyHelperPaginatedListView(HandyHelperListView):
    paginate_by = 10
    elided_on_each_side = elided_on_ends = 1
    include_total = True

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset if queryset.ordered else queryset.order_by("pk")

    def paginate_queryset(self, queryset, page_size):
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(self.request.GET.get("page", 1))
        page.adjusted_elided_pages = paginator.get_elided_page_range(
            page.number, on_each_side=self.elided_on_each_side, on_ends=self.elided_on_ends
        )
        return paginator, page, page.object_list, page.has_other_pages()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            queryset=context["page_obj"], is_paginated_view=True, include_total=self.include_total
        )
        return context
