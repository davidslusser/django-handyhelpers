from collections import OrderedDict
from rest_framework import status
from rest_framework_filters.filters import RelatedFilter
from django.http import JsonResponse
from django.conf import settings


class InvalidLookupMixin:
    """ A mixin for Django Rest Framework viewsets to check query parameters and return an error if any query parameter
    is not a included in defined in a filter_class (typically defined in your filterset), and element of
    filter_fields (typically set in your viewset), or a valid model field.
    Order of precedence is: filter_class, filterset_fields, filter_fields, model field.

    class parameters:
        request          - request object (as provided by Viewset)
        model            - django model (as provided by Viewset)
        queryset         - django queryset (as provided by Viewset)
        filterset_class  - optional filterset_class (as provided by Viewset)
        filter_class     - optional filter_class (as provided by Viewset)
        filterset_fields - optional filterset_fields (as provided by Viewset)
        filter_fields    - optional filter_fields (as provided by Viewset)

    example usage:
        class MyModelViewSet(InvalidLookupMixin, viewsets.ReadOnlyModelViewSet):
    """
    request = None
    model = None
    queryset = None
    filter_class = None
    filterset_class = None
    filterset_fields = []
    filter_fields = []

    def get_lookup_expression(self, fs_filter, related_field=None, lookup_expression_list=None):
        """
        get lookup expressions as defined in a FilterSet filter

        Args:
            fs_filter:              list of filters as defined in the filterset
            related_field:          related field as defined in filterset
            lookup_expression_list: list of lookup expressions as defined for a field in a filterset

        Returns:
            list of filtered lookup expressions
        """
        if not lookup_expression_list:
            lookup_expression_list = []
        for i, j in fs_filter.items():
            if isinstance(j, RelatedFilter):
                if related_field:
                    # protect against recursion if filter field is the same as the related field
                    if related_field.endswith(f'__{i}'):
                        return lookup_expression_list
                    next_related_field = f'{related_field}__{i}'
                else:
                    next_related_field = i
                self.get_lookup_expression(j.filterset.get_filters(), related_field=next_related_field,
                                           lookup_expression_list=lookup_expression_list)
            else:
                if related_field:
                    expression = '{}__{}'.format(related_field, i)
                    if expression not in lookup_expression_list:
                        lookup_expression_list.append(expression)
                else:
                    if i not in lookup_expression_list:
                        lookup_expression_list.append(i)
        return lookup_expression_list

    def dispatch(self, request, *args, **kwargs):
        for field, val in self.request.GET.dict().items():
            # ignore the '!' in 'field!=value' if filters are used
            field = field.rstrip('!')
            if field in getattr(settings, 'INVALID_LOOKUP_SKIP_LIST',
                                ['offset', 'limit', 'format', 'fields', 'omit', 'expand', 'disable_pagination']):
                continue

            if self.filterset_class:
                # if filterset_class is available, return error if any query parameter is not a lookup expression
                valid_fields = self.get_lookup_expression(self.filterset_class.get_filters())
                if field not in valid_fields:
                    return JsonResponse(data={'detail': f'{field} is not a valid filter field'},
                                        status=status.HTTP_404_NOT_FOUND)

            elif self.filter_class:
                # if filter_class is available, return error if any query parameter is not a lookup expression
                valid_fields = self.get_lookup_expression(self.filter_class.get_filters())
                if field not in valid_fields:
                    return JsonResponse(data={'detail': f'{field} is not a valid filter field'},
                                        status=status.HTTP_404_NOT_FOUND)

            elif self.filterset_fields:
                # if filterset_fields are available, return error if any query parameter is not a filter field
                if field not in self.filterset_fields:
                    return JsonResponse(data={'detail': f'{field} is not valid field. Filterable fields are: '
                                                        f'{self.filterset_fields}'},
                                        status=status.HTTP_404_NOT_FOUND)

            elif self.filter_fields:
                # if filter_fields are available, return error if any query parameter is not an available filter field
                if field not in self.filter_fields:
                    return JsonResponse(data={'detail': f'{field} is not valid field. Filterable fields are: '
                                                        f'{self.filter_fields}'},
                                        status=status.HTTP_404_NOT_FOUND)

            else:
                # if neither filter_class nor filterset_fields are available, return error if any query parameter is
                # not a field in the model
                if field.split('__')[0] not in [i.name for i in self.model._meta.fields +
                                                                self.model._meta.many_to_many]:
                    return JsonResponse(data={'detail': f'{field} is not a valid field in {self.model.__name__}'},
                                        status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)


class PaginationControlMixin:
    """ A mixin for Django Rest Framework viewsets that allows pagination to be disabled by including a
    specific query parameter. Default query parameter for disabling pagination is 'disable_pagination' and this
    can be modified by setting the PAGINATION_CONTROL_PARAMETER variable to the desired value in django settings. """

    def dispatch(self, request, *args, **kwargs):
        disable_pagination_param = getattr(settings, 'PAGINATION_CONTROL_PARAMETER', 'disable_pagination')
        if disable_pagination_param in self.request.GET.dict():
            setattr(self, 'pagination_class', None)
        return super().dispatch(request, *args, **kwargs)


class ExcludeNullMixin:
    """ A mixin to remove fields if value is None. """
    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])
