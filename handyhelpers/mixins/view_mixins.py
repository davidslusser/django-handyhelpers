"""Filtering and HTMX request mixins."""

from django.conf import settings
from django.core.exceptions import EmptyResultSet, FieldError, ImproperlyConfigured, ValidationError
from django.utils.html import format_html_join

from handyhelpers.utils import InvalidFilter, RequestStateMixin, update_query


class FilterByQueryParamsMixin(RequestStateMixin):
    """Apply ORM lookups, rejecting invalid filters instead of showing unfiltered data.

    Extend ``filter_control_params`` in a subclass for non-filter query parameters.
    A provided ``filter_fields`` iterable restricts allowed lookup roots.
    """

    queryset = None
    page_description = None
    distinct = False
    filter_fields = None
    filter_control_params = frozenset(
        {
            "page",
            "page_description",
            "distinct",
            "display",
            "offset",
            "limit",
            "format",
            "fields",
            "omit",
            "expand",
            "disable_pagination",
        }
    )

    def get_filter_queryset(self):
        if self.queryset is not None:
            return self.queryset.all()
        if getattr(self, "model", None) is not None:
            return self.model._default_manager.all()
        raise ImproperlyConfigured("Set model or queryset on this view.")

    def filter_by_query_params(self, parameters=None):
        queryset = self.get_filter_queryset()
        params = self.request.GET if parameters is None else parameters
        filters = {}
        for key, value in params.items():
            if key in self.filter_control_params:
                continue
            if self.filter_fields is not None and key.split("__")[0] not in self.filter_fields:
                raise InvalidFilter(f"{key} is not an allowed filter field")
            if value == "None":
                value = None
            elif isinstance(value, str) and value.lower() in {"true", "false"}:
                value = value.lower() == "true"
            if key.endswith("__in") and isinstance(value, str):
                value = value.split(",")
            filters[key] = value
        if not self.page_description:
            self.page_description = params.get("page_description")
        try:
            result = queryset.filter(**filters)
            # Compilation also validates invalid RHS values for lazy querysets.
            result.query.get_compiler(using=result.db).as_sql()
        except EmptyResultSet:
            pass
        except (FieldError, ValueError, TypeError, ValidationError) as error:
            raise InvalidFilter(f"Invalid filter: {error}") from error
        distinct = params.get("distinct", False)
        if isinstance(distinct, str):
            distinct = distinct.lower() not in {"false", "0", ""}
        if distinct or self.distinct or getattr(settings, "HH_FILTERBYQUERYPARAM_DISTINCT", False):
            result = result.distinct()
        return result


class TimestampFilterMixin(FilterByQueryParamsMixin):
    """Add a validated timestamp filter form and description to a view context."""

    filter_form = None
    root_list_url = "/"
    root_queryset = None
    context = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.filter_view()
        except InvalidFilter as error:
            from django.http import HttpResponseBadRequest

            return HttpResponseBadRequest(str(error))
        return super().dispatch(request, *args, **kwargs)

    def filter_view(self):
        from handyhelpers.forms import TimestampFilter

        form_class = self.filter_form or TimestampFilter
        form = form_class(self.request.GET or None)
        if form.is_bound and not form.is_valid():
            raise InvalidFilter(form.errors.as_text())
        self.queryset = self.root_queryset
        self.root_queryset = self.filter_by_query_params()
        self.root_list_url = update_query(self.root_list_url, self.request.GET.dict())
        self.context = dict(self.context or {})
        labels = []
        for name, label in [("created_at", "Created"), ("updated_at", "Updated")]:
            if any(key.startswith(name + "__") for key in self.request.GET):
                labels.append(
                    (
                        label,
                        self.request.GET.get(name + "__gte", ""),
                        self.request.GET.get(name + "__lte", ""),
                    )
                )
        self.context["subtitle"] = format_html_join(", ", "{}: {} – {}", labels)
        self.context["filter_form"] = form


class HtmxViewMixin(RequestStateMixin):
    """Identify HTMX requests, treating HX-Request: false as a regular request."""

    def is_htmx(self):
        result = self.request.headers.get("HX-Request", "").lower() == "true"
        self.request.is_htmx = result
        return result
