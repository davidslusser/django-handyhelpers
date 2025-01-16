from django.conf import settings


class FlexFieldsMixin:
    """A serializer mixin that allow filtering or omitting fields by query parameters"""

    query_params: dict = {}

    def __init__(self, *args, **kwargs) -> None:
        request = kwargs.get("context", {}).get("request", None)

        if request:
            self.query_params = request.query_params
        super().__init__(*args, **kwargs)

    def get_fields(self):
        fields = super().get_fields()
        if self.query_params:
            fields_param: str = getattr(settings, "HH_FIELDS_PARAM", "fields")
            omit_param: str = getattr(settings, "HH_OMIT_PARAM", "omit")
            requested_fields = self.query_params.get(fields_param, None)
            omitted_fields = self.query_params.get(omit_param, None)
            if requested_fields:
                return {
                    key: value
                    for key, value in fields.items()
                    if key in requested_fields.split(",")
                }
            elif omitted_fields:
                return {
                    key: value
                    for key, value in fields.items()
                    if key not in omitted_fields.split(",")
                }
        return fields
