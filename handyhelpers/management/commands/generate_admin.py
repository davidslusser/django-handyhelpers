from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.conf import settings
from jinja2 import Template
import os

__version__ = '0.0.2'


class Command(BaseCommand):
    help = "Generate admin.py file, based on a jinja2 template, for a given app"

    def __init__(self):
        self.opts = None
        self.app = None
        self.model_list = None
        super(Command, self).__init__()

    def add_arguments(self, parser):
        """ define command arguments """
        parser.add_argument('app', type=str, help='name of the django app')
        parser.add_argument('--template', type=str, help='path to Jinja template used to create admin.py file')
        parser.add_argument('--output_file', type=str, help='path of output file to create')

    def handle(self, *args, **options):
        """ command entry point """
        if options['app'] not in settings.INSTALLED_APPS:
            raise CommandError(f"'{options['app']}' is not an available application in this project")

        self.opts = options
        self.app = options['app']
        self.get_model_list()
        self.get_admin_template()
        self.get_output_file()
        self.build_admin()
        self.stdout.write(self.style.SUCCESS(f"{self.opts['output_file']} generated!"))

    def get_output_file(self):
        """ return the full path of the generated file """
        if not self.opts['output_file']:
            self.opts['output_file'] = f'{os.getcwd()}/{self.app}/admin.py'

    def get_admin_template(self):
        """ return the full path of the jinja template to use in creating the admin.py file """
        if not self.opts['template']:
            self.opts['template'] = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                 'admin_templates', 'admin.jinja')

    def get_model_list(self):
        """ return a list of all models in application """
        app = apps.get_app_config(self.app)
        self.model_list = list(app.get_models())

    @staticmethod
    def get_model_field_names(model, exclude_list=()):
        """ return a list of field names for a given model """
        return [i.name for i in model._meta.fields if type(i).__name__ not in exclude_list]

    def build_admin(self):
        """ build the admin.py file """
        model_fields = {}
        for model in self.model_list:
            model_fields[model.__name__] = self.get_model_field_names(model)

        data = {'model_list': self.model_list,
                'app_name': self.app,
                'models_file': 'models',
                'model_data': self.get_models_and_fields(),
                }

        with open(self.opts['template']) as f:
            template = Template(f.read())
        file_text = template.render(data)

        with open(self.opts['output_file'], 'w') as f:
            f.write(file_text)

    @staticmethod
    def get_display_fields(model, exclude_field_list=()):
        """ build and return a list of 'list_display' to be used in admin.py for a given model """
        return [i.name for i in model._meta.fields if i.get_internal_type() not in exclude_field_list]

    @staticmethod
    def get_search_fields(model, exclude_field_list=('AutoField', 'BooleanField', 'DateTimeField', 'ForeignKey')):
        """ build and return a list of 'search_fields' to be used in admin.py for a given model """
        return [i.name for i in model._meta.fields if i.get_internal_type() not in exclude_field_list]

    @staticmethod
    def get_filter_fields(model, include_field_list=('BooleanField', 'ForeignKey', 'CharField')):
        """ build and return a list of 'filter_fields' to be used in admin.py for a given model """
        return_list = []
        for i in model._meta.fields:
            field_type = i.get_internal_type()
            if field_type in include_field_list:
                if field_type == 'CharField' and not i.choices:
                    continue
                elif field_type == 'CharField' and i.choices:
                    return_list.append(i.name)
                else:
                    return_list.append(i.name)
        return return_list

    def get_models_and_fields(self):
        return_data = {}
        for model in self.model_list:
            return_data[model.__name__] = {'display_fields': self.get_display_fields(model),
                                           'search_fields': self.get_search_fields(model),
                                           'filter_fields': self.get_filter_fields(model),
                                           }
        return return_data
