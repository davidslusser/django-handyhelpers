# django-handy-helpers

A collection of handy utilities to support django operations


# How to Install
1. pip install django-handyhelpers
2. add 'djangohelpers' to your INSTALLED_APPS (for management commands)


# Management Commands 

### DRF Generator
Django-handyhelpers includes manage.py commands to generate DRF files (api views, serializers, urls) for a given app in your project.
This is done using jinja templates that define the structure of each file. Default templates are provided, and custom templates 
can be provided in the command. By default, all models and models fields are included.  

Example command:
    ./manage.py generate_drf <my_app> --serializer
    ./manage.py generate_drf <my_app> --serializer --serializer_template <my_custom_template>

** see ./manage.py generate_drf --help for a full list of options

