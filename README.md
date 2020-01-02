# django-handy-helpers

| | | |
|--------------|------|---|
| Author       | David Slusser |   |
| Description  | A collection of handy utilities to support django projects |   |
| Requirements | `Python 3.x`<br>`Django 2.2.x+` |   |



# How to Install
1. pip install django-handyhelpers
2. add 'djangohelpers' to your INSTALLED_APPS (for management commands and templates)


# Management Commands 

### DRF Generator
Django-handyhelpers includes manage.py commands to generate DRF files (api views, serializers, urls) for a given app in your project.
This is done using jinja templates that define the structure of each file. Default templates are provided, and custom templates 
can be provided in the command. By default, all models and models fields are included.  

Example command:
    ./manage.py generate_drf <my_app> --serializer
    ./manage.py generate_drf <my_app> --serializer --serializer_template <my_custom_template>

** see ./manage.py generate_drf --help for a full list of options



### Admin Generator
Included with django-handyhelpers are manage.py commands to auto-generate an admin.py file for a given application in 
your project. This is done using a jinja template that defines the structure of the admin.py file. A default template is 
provided. 

Example command:
    ./manage.py generate_admin <my_app>
    ./manage.py generate_admin <my_app> --template <my_custom_template>
    
** see ./manage.py generate-admin --help for a full list of options     
