"""Strict filter validation after DRF authenticates a request."""

from django.conf import settings

from handyhelpers.utils import optional_import

exceptions = optional_import("rest_framework.exceptions", "api")
filters = optional_import("django_filters.rest_framework", "api")


class InvalidLookupMixin:
    """Validate filter names and values using django-filter's DRF integration."""

    filter_control_params = frozenset(
        {
            "page",
            "offset",
            "limit",
            "format",
            "fields",
            "omit",
            "expand",
            "ordering",
            "search",
            "disable_pagination",
        }
    )

    def filter_queryset(self, queryset):
        backend = filters.DjangoFilterBackend()
        filterset_class = backend.get_filterset_class(self, queryset)
        if filterset_class is None:

            class ModelFilterSet(filters.FilterSet):
                class Meta:
                    model = queryset.model
                    fields = [field.name for field in model._meta.fields]

            filterset_class = ModelFilterSet
        allowed = set(filterset_class.base_filters)
        controls = set(self.filter_control_params) | set(
            getattr(settings, "INVALID_LOOKUP_SKIP_LIST", ())
        )
        controls.add(getattr(settings, "PAGINATION_CONTROL_PARAMETER", "disable_pagination"))
        invalid = set(self.request.query_params) - allowed - controls
        if invalid:
            raise exceptions.ValidationError(
                {"detail": f"Invalid filter fields: {', '.join(sorted(invalid))}"}
            )
        filterset = filterset_class(
            data=self.request.query_params, queryset=queryset, request=self.request
        )
        if not filterset.is_valid():
            raise exceptions.ValidationError(filterset.errors)
        return super().filter_queryset(filterset.qs)


class PaginationControlMixin:
    def paginate_queryset(self, queryset):
        param = getattr(settings, "PAGINATION_CONTROL_PARAMETER", "disable_pagination")
        if self.request.query_params.get(param, "").lower() in {"true", "1", "yes"}:
            return None
        return super().paginate_queryset(queryset)
