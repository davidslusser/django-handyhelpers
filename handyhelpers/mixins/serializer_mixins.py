"""Serializer field selection and null suppression."""

from django.conf import settings


class FlexFieldsMixin:
    def __init__(self, *args, **kwargs):
        request = kwargs.get("context", {}).get("request")
        self.query_params = request.query_params if request is not None else {}
        super().__init__(*args, **kwargs)

    def get_fields(self):
        fields = super().get_fields()
        requested = self.query_params.get(getattr(settings, "HH_FIELDS_PARAM", "fields"))
        omitted = self.query_params.get(getattr(settings, "HH_OMIT_PARAM", "omit"))
        if requested:
            names = set(requested.split(","))
            fields = {name: field for name, field in fields.items() if name in names}
        elif omitted:
            names = set(omitted.split(","))
            fields = {name: field for name, field in fields.items() if name not in names}
        return fields


class ExcludeNullMixin:
    def to_representation(self, instance):
        return {
            key: value
            for key, value in super().to_representation(instance).items()
            if value is not None
        }
