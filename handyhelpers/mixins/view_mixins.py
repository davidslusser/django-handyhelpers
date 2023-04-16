from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.fields import ReverseGenericManyToOneDescriptor
from django.core.exceptions import FieldError

import handyhelpers.forms


class FilterByQueryParamsMixin:
    """ Mixin used to evaluate query parameters provided in the URL and update a queryset accordingly. This is typically
    used on list views. Query parameters passed must be valid model fields. Invalid parameters are ignored.

    class parameters:
        request          - request object
        queryset         - django queryset
        page_description - optional parameter used to describe page; typically used as a page subtitle
        distinct         - optional parameter to make queryset include only distinct results

    example usage:
        class HandyHelperGenericBaseListView(FilterByQueryParamsMixin, ListView)
    """

    request = None
    queryset = None
    page_description = None
    distinct = None

    def filter_by_query_params(self):
        """
        Description:
            Filters a queryset by query_params in the URL

        Returns:
            filtered queryset
        """
        force_distinct = any([
            'distinct' in self.request.GET.dict(),
            self.distinct,
            getattr(settings, 'HH_FILTERBYQUERYPARAM_DISTINCT', False),
            ])

        # pass a description to the view if included as a query parameter
        if not self.page_description and 'page_description' in self.request.GET.dict():
            self.page_description = self.request.GET.dict().get('page_description', None)

        # build a dictionary of valid model fields
        filter_dict = {}
        model = self.queryset.model
        try:
            for arg, val in self.request.GET.dict().items():
                field = arg.split('__')[0]
                field_is_generic = type(getattr(model, field, None)) == ReverseGenericManyToOneDescriptor
                if field_is_generic:
                    force_distinct = True
                if field not in [i.name for i in model._meta.fields +
                                                 model._meta.many_to_many +
                                                 model._meta.related_objects] + \
                        getattr(settings, 'HH_QUERY_PARAM_PREFIXES', ['eav']) and not field_is_generic:
                    continue
                if val is not None:
                    if val == 'None':
                        val = None
                    elif val in 'TruetrueTRUE':
                        val = True
                    elif val in 'FalsefalseFALSE':
                        val = False
                    filter_dict[arg] = val
            if force_distinct:
                return self.queryset.filter(**filter_dict).distinct()
            return self.queryset.filter(**filter_dict)
        except AttributeError:
            if getattr(settings, 'HH_FILTERBYQUERYPARAM_NO_FILTER_ON_FAIL', True):
                return self.queryset
            return model.objects.none()
        except FieldError:
            if getattr(settings, 'HH_FILTERBYQUERYPARAM_NO_FILTER_ON_FAIL', False):
                return self.queryset
            return model.objects.none()


class TimestampFilterMixin:
    """ Mixin used to add ability to filter data by created_at/updated_at date ranges. This mixin expects 'created_at'
    and 'updated_at' time stamps and uses __gte and __lte filters.

    class parameters:
        request          - request object
        filter_form      - django form with created_at/updated_at inputs
        root_list_url    - root url to list view
        root_queryset    - django queryset
        show_messages    - display a message if filter fails

    example usage:
        class MyCoolView(TimestampFilterMixin, View):
            filter_form = MyFilterClass
            root_list_url = '/myapp/list_view_for_my_model?'
            root_queryset = MyModel.objects.all()
            ...
    """
    request = None
    filter_form = handyhelpers.forms.TimestampFilter
    root_list_url = None
    root_queryset = None
    context = dict()
    show_messages = True

    def dispatch(self, request, *args, **kwargs):
        self.filter_view()
        return super().dispatch(request, *args, **kwargs)

    def filter_view(self):
        query_dict = dict()
        subtitle_list = list()
        query_params = self.request.GET.dict()
        populated_query_param_list = [k for k, v in query_params.items() if v]

        # build query dictionary and list url
        for k, v in query_params.items():
            if v:
                query_dict[k] = v
                self.root_list_url += f'{k}={v}&'

        # add timestamp fields to subtitle
        look_for = 'created_at'
        if [i for i in populated_query_param_list if look_for in i]:
            subtitle_list.append(
                f'<b>Created:</b> <i>{query_params.get("created_at__gte")} - {query_params.get("created_at__lte")}</i>')
        look_for = 'updated_at'
        if [i for i in populated_query_param_list if look_for in i]:
            subtitle_list.append(
                f'<b>Updated:</b> <i>{query_params.get("updated_at__gte")} - {query_params.get("updated_at__lte")}</i>')
        self.context['subtitle'] = ', '.join(subtitle_list)

        # filter records based on parsed query parameters
        try:
            if query_dict:
                self.root_queryset = self.root_queryset.filter(**query_dict)
        except FieldError:
            if self.show_messages:
                messages.add_message(self.request, messages.ERROR, f'invalid filter; all data will be displayed',
                                     extra_tags='alert-danger', )
            else:
                pass

        # add filter form
        if self.filter_form:
            self.context['filter_form'] = self.filter_form(self.request.POST or None, initial=query_params)
