.. _features:

========
Features
========

This document details the features currently available in django-handyhelpers.


Mangement Commands
==================

Admin Generator
---------------

Included with django-handyhelpers are manage.py commands to auto-generate an admin.py file for a given application in
your project. This is done using a jinja template that defines the structure of the admin.py file. A default template is
provided.

Command Examples:

** use the --help parameter for a full list of options

.. code-block:: python

    manage.py generate_admin <my_app>
    manage.py generate_admin <my_app> --template <my_custom_template>
    manage.py generate-admin --help
..


DRF Generator
-------------

Django-handyhelpers includes manage.py commands to generate DRF files (api views, serializers, urls) for a given app in your project.
This is done using jinja templates that define the structure of each file. Default templates are provided, and custom templates
can be provided in the command. By default, all models and models fields are included.

Command Examples:

** use the --help parameter for a full list of options

.. code-block:: python

    manage.py generate_drf <my_app> --serializer
    manage.py generate_drf <my_app> --serializer --serializer_template <my_custom_template>
    manage.py generate_drf --help
..


Views
=====

List Views
----------

Base list views are also included which use the FilterByQueryParamsMixin and generic templates to further simplify your
list views. Every parameter can be overwritten to fully customize to your needs. The HandyHelperListView uses a
Bootstrap-based template to list your results; simply include a html template with a table formatted for your model and
include it in the table parameter. The HandyHelperListPlusCreateView has all the features as the HandyHelperListView
but also allows for a form to create new records. The HandyHelperListPlusFilterView has all the features as the
HandyHelperListView but also allows for a form to filter records. The HandyHelperListPlusCreateAndFilterView allows for
create and filter forms. To utilize the filter views, you must include handyhelpers urls in your project level urls:

.. code-block:: python

    path('handyhelpers/', include('handyhelpers.urls'), ),

..

Examples:

.. code-block:: python

    from handyhelpers.views.gui import HandyHelperBaseListView

    class ListProjects(HandyHelperBaseListView):
        queryset = Project.objects.all()
        title = 'Projects'
        page_description = 'my cool projects'
        table = 'table/table_projects.htm'

..

.. code-block:: python

    from handyhelpers.views.gui import HandyHelperListPlusCreateView

    class ListProjects(HandyHelperBaseCreateListView):
        queryset = Project.objects.all()
        title = 'Projects'
        page_description = 'my cool projects'
        table = 'table/table_projects.htm'
        create_form_obj = ProjectForm
        create_form_url = '/hostmgr/create_project/'
        create_form_title = '<b>Add Project: </b><small> </small>'
        create_form_modal = 'add_project'
        create_form_link_title = 'add project'

..

.. code-block:: python

    from handyhelpers.views.gui import HandyHelperListPlusFilterView

    class ListProjects(HandyHelperListPlusFilterView):
        queryset = Project.objects.all()
        title = 'Projects'
        page_description = 'my cool projects'
        table = 'table/table_projects.htm'
        filter_form_obj = ProjectForm
        filter_form_url = '/hostmgr/filter_project/'
        filter_form_title = '<b>Filter Projects: </b><small> </small>'
        filter_form_modal = 'filter_project'
        filter_form_link_title = 'filter project'
        filter_form_tool_tip = 'filter project'

Export Views
------------

Export views are available to easily render a queryset to csv or xls file. These views include the
FilterByQueryParamsMixin, making filtered outputs available. These export views can be used as follows:

.. code-block:: python

    from handyhelpers.views import CsvExportView, ExcelExportView

    class ExportMyModelCsv(CsvExportView):
        queryset = MyModel.objects.all()


    class ExportMyModelXls(ExcelExportView):
        queryset = MyModel.objects.all()

..


Mixins
======

FilterByQueryParamsMixin
------------------------

The FilterByQueryParamsMixin allows a list view to show a filtered queryset results by query_params provided in the URL.

Example:

.. code-block:: python

    from handyhelpers.mixins.view_mixins import FilterByQueryParamsMixin

    class ListProjects(FilterByQueryParamsMixin, ListView):
        def get(self, request, *args, **kwargs):
            return render(request, "my_template.html", context={'queryset': self.filter_by_query_params()})

..

InAllGroups
-----------
The InAllGroups permissions mixin restricts access based on request method and user group. User must be in ALL required groups.

optional: When settings variable MESSAGE_ON_PERMISSION_DENY is set to True, an alert will be sent via messages and
redirect will be to the HTTP_REFERER instead of redirecting to the LOGIN_URL.

Usage:
    Add as mixin to class definition and put the following in your viewset:

.. code-block:: python

    from handyhelpers.permissions import InAllGroups

    def MyView(InAllGroups, View):
        permission_dict = {'POST': ['site_operators', 'site_admins'], 'GET': ['site_operators']}
        ...

..

InAnyGroup
----------
The InAnyGroup permission mixin will restrict access based on request method and user group. User can be in ANY required group.

optional: When settings variable MESSAGE_ON_PERMISSION_DENY is set to True, an alert will be sent via messages and
redirect will be to the HTTP_REFERER instead of redirecting to the LOGIN_URL.


Usage:
    Add as mixin to class definition and put the following in your viewset:

.. code-block:: python

    from handyhelpers.permissions import InAnyGroup

    def MyView(InAnyGroup, View):
        permission_dict = {'POST': ['site_admins'], 'GET': ['site_admins', 'site_operators']}

..

InvalidLookupMixin
------------------

By default, drf viewsets will ignore an invalid field, filter, or lookup expression, causing the API to return all
records. As this might not be the desired behaviour, handyhelpers provides a mixin for Django Rest Framework viewsets
that checks query parameters and returns an error if any query parameter is not a included in defined in a filter_class
(typically defined in your filterset), and element of filter_fields (typically set in your viewset), or a valid model field.
Order of precedence is: filterset_class,  filter_class, filterset_fields, filter_fields, model field.

Examples:

.. code-block:: python

    from handyhelpers.mixins.viewset_mixins import InvalidLookupMixin

    class MyModelViewSet(InvalidLookupMixin, viewsets.ReadOnlyModelViewSet):

..

PaginationControlMixin
----------------------
A mixin for Django Rest Framework viewsets that allows pagination to be disabled by including a specific query
parameter. Default query parameter for disabling pagination is 'disable_pagination' and this can be modified by
setting the PAGINATION_CONTROL_PARAMETER variable to the desired value in django settings.

Examples:

.. code-block:: python

    from handyhelpers.mixins.viewset_mixins import PaginationControlMixin

    class MyModelViewSet(PaginationControlMixin, viewsets.ReadOnlyModelViewSet):

..
