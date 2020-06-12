.. _features:


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


Views and Mixins
================

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

Base list views are also included which use the FilterByQueryParamsMixin and generic templates to further simplify your
list views. Every parameter can be overwritten to fully customize to your needs. The HandyHelperBaseListView uses a
Bootstrap-based template to list your results; simply include a html template with a table formatted for your model and
include it in the table parameter. The HandyHelperBaseCreateListView has all the features as the HandyHelperBaseListView
but also allows for a form to create new records.

Examples:

.. code-block:: python

    from handyhelpers.views.gui import HandyHelperBaseListView

    class ListProjects(HandyHelperBaseListView):
        queryset = Project.objects.all()
        title = "Projects"
        page_description = "my cool projects"
        table = "table/table_projects.htm"

..

.. code-block:: python

    from handyhelpers.views.gui import HandyHelperBaseCreateListView

    class ListProjects(HandyHelperBaseCreateListView):
        queryset = Project.objects.all()
        title = "Projects"
        page_description = "my cool projects"
        table = "table/table_projects.htm"
        create_form_obj = ProjectForm
        create_form_url = '/hostmgr/create_project/'
        create_form_title = "<b>Add Project: </b><small> </small>"
        create_form_modal = "add_project"
        create_form_link_title = "add project"

..

Export views are available to easily render a queryset to csv or xls file. These views include the
FilterByQueryParamsMixin, making filtered outputs available. These export views can be used as follows:

.. code-block:: python

    from handyhelpers.views import CsvExportView, ExcelExportView

    class ExportMyModelCsv(CsvExportView):
        queryset = MyModel.objects.all()


    class ExportMyModelXls(ExcelExportView):
        queryset = MyModel.objects.all()

..


InvalidLookupMixin
------------------

By default, drf viewsets will ignore an invalid field, filter, or lookup expression, causing the API to return all
records. As this might not be the desired behaviour, handyhelpers provides a mixin for Django Rest Framework viewsets
that checks query parameters and returns an error if any query parameter is not a included in defined in a filter_class
(typically defined in your filterset), and element of filter_fields (typically set in your viewset), or a valid model field.
Order of precedence is: filter_class, filter_fields, model field.

Examples:

.. code-block:: python

    from handyhelpers.mixins.viewset_mixins import InvalidLookupMixin

    class MyModelViewSet(InvalidLookupMixin, viewsets.ReadOnlyModelViewSet):

..
