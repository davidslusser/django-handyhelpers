from rest_framework import status
from rest_framework_filters.filters import RelatedFilter
from django.http import JsonResponse


class InvalidLookupMixin:
    """ A mixin for Django Rest Framework viewsets to check query parameters and return an error if any query parameter
    is not a included in defined in a filter_class (typically defined in your filterset), and element of
    filter_fields (typically set in your viewset), or a valid model field.
    Order of precedence is: filter_class, filter_fields, model field.

    example usage:
        class MyModelViewSet(InvalidLookupMixin, viewsets.ReadOnlyModelViewSet):
    """
    request = None
    model = None
    queryset = None
    filter_class = None
    filter_fields = []

    def get_lookup_expression(self, fs_filter, related_field=None, lookup_expression_list=None):
        """ get lookup expressions as defined in a FilterSet filter """
        if not lookup_expression_list:
            lookup_expression_list = []
        for i, j in fs_filter.items():
            if isinstance(j, RelatedFilter):
                lookup_expression_list.append(i)
                self.get_lookup_expression(j.filterset.get_filters(), related_field=i,
                                           lookup_expression_list=lookup_expression_list)
            else:
                if related_field:
                    lookup_expression_list.append('{}__{}'.format(related_field, i))
                else:
                    lookup_expression_list.append(i)
        return lookup_expression_list

    def dispatch(self, request, *args, **kwargs):
        for field, val in self.request.GET.dict().items():
            if self.filter_class:
                # if filter_class is available, return error if any query parameter is not a lookup expression
                valid_fields = self.get_lookup_expression(self.filter_class.get_filters())
                if field not in valid_fields:
                    return JsonResponse(data={'detail': '{} is not a defined filter field in {}'
                                        .format(field, self.model.__name__)}, status=status.HTTP_404_NOT_FOUND)

            elif self.filter_fields:
                # if filter_fields are available, return error if any query parameter is not an available filter field
                if field not in self.filter_fields:
                    return JsonResponse(data={'detail': '{} is not a defined filter field in {}'
                                        .format(field, self.model.__name__)}, status=status.HTTP_404_NOT_FOUND)

            else:
                # if neither filter_class nor filter_fields are available, return error if any query parameter is
                # not a field in the model
                if field.split('__')[0] not in [i.name for i in self.model._meta.fields +
                                                                self.model._meta.many_to_many]:
                    return JsonResponse(data={'detail': '{} is not a valid field in {}'
                                        .format(field, self.model.__name__)}, status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)
