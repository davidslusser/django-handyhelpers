
class FilterByQueryParamsMixin:
    request = None
    queryset = None
    page_description = None

    def filter_by_query_params(self):
        """
        Description:
            Filters a queryset by query_params in the URL

        Returns:
            filtered queryset
        """
        # pass a description to the view if included as a query parameter
        if not self.page_description and 'page_description' in self.request.GET.dict():
            self.page_description = self.request.GET.dict().get('page_description', None)

        # build a dictionary of valid model fields
        filter_dict = {}
        model = self.queryset.model
        for field, val in self.request.GET.dict().items():
            if field.split("__")[0] not in [i.name for i in model._meta.fields + model._meta.many_to_many]:
                continue
            if val is not None:
                if val == 'None':
                    val = None
                filter_dict[field] = val
        return self.queryset.filter(**filter_dict)
