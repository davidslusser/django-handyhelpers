# django-handy-helpers


| | | |
|--------------|------|---|
| Author       | David Slusser |   |
| Description  | A collection of handy utilities to support django projects |   |
| Requirements | `Python 3.x`<br>`Django 2.2.x` |   |


# Documentation
Full documentation can be found on http://django-handyhelpers.readthedocs.org. 
Documentation source files are available in the docs folder.


# How to Install
The django-userextensions package is available on Python Package Index (PyPI) and can be installed via pip:

    pip install django-handyhelpers
    

add 'handyhelpers' to your INSTALLED_APPS (for management commands and templates)

    INSTALLED_APPS = [
        ...
        'handyhelpers',
    ]


# Management Commands 

### DRF Generator
Django-handyhelpers includes manage.py commands to generate DRF files (api views, serializers, urls) for a given app in your project.
This is done using jinja templates that define the structure of each file. Default templates are provided, and custom templates 
can be provided in the command. By default, all models and models fields are included.  

Example command:

    manage.py generate_drf <my_app> --serializer
    manage.py generate_drf <my_app> --serializer --serializer_template <my_custom_template>

** use the --help parameter for a full list of options

    manage.py generate_drf --help



### Admin Generator
Included with django-handyhelpers are manage.py commands to auto-generate an admin.py file for a given application in 
your project. This is done using a jinja template that defines the structure of the admin.py file. A default template is 
provided. 

Example command:

    manage.py generate_admin <my_app>
    manage.py generate_admin <my_app> --template <my_custom_template>
    
** use the --help parameter for a full list of options
 
    manage.py generate-admin --help     


# Mixins

### FilterByQueryParamsMixin
Allows your list views to be filtered by query parameters.


### InvalidLookupMixin
Returns an applicable error, instead of results based on an unfiltered queryset, if a provided  lookup expression, 
filter, or model field is invalid.   

