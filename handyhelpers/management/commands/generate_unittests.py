from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.conf import settings
from jinja2 import Template
import os

__version__ = '0.0.2'


class Command(BaseCommand):
    help = "Generate unittest file, based on a jinja2 template, for a given app"

    def __init__(self):
        self.opts = None
        self.app = None
        self.model_list = None
        super(Command, self).__init__()

    def add_arguments(self, parser):
        """ define command arguments """
        parser.add_argument('app', type=str, help='name of the django app')
        parser.add_argument('--test_type', type=str, help='django construct to create tests for (model, view, viewset)')
        parser.add_argument('--template', type=str, help='path to Jinja template used to create unittest file')
        parser.add_argument('--output_path', type=str, default='.', help='path where files should be created')
        parser.add_argument('--output_file', type=str, default=None, help='fully qualified name of file to be created; '
                                                                          'only use this when generating one file')

    def handle(self, *args, **options):
        """ command entry point """
        if options['app'] not in settings.INSTALLED_APPS:
            raise CommandError(f"'{options['app']}' is not an available application in this project")

        self.opts = options
        self.app = options['app']
        self.get_model_list()

        # build model unittests
        if 'model' in options['test_type']:
            self.build_model_unittests(output_path=options['output_path'],
                                       output_file=options['output_file'],
                                       template_file=options['template'])
        else:
            print('only model test are currently supported')

    @staticmethod
    def get_model_field_names(model, exclude_list=()):
        """ return a list of field names for a given model """
        return [i.name for i in model._meta.fields if type(i).__name__ not in exclude_list]

    def get_model_list(self):
        """ return a list of all models in application """
        app = apps.get_app_config(self.app)
        self.model_list = sorted(list(app.get_models()), key=lambda x: x._meta.model_name)

    def build_model_unittests(self, output_path=None, output_file=None, template_file=None):
        """ build unittest file for models """
        if not template_file:
            template_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         'unittest_templates', 'model_crud_update_all_fields.jinja')

        if output_file:
            output_path = output_file
        elif not output_path:
            output_path = 'test_model_crud.py'
        elif os.path.isdir(output_path):
            output_path = f'{output_path}/test_model_crud.py'

        auditlog_models = []
        if apps.is_installed('auditlog'):
            try:
                from auditlog.registry import auditlog
                auditlog_models = auditlog.get_models()
            except ModuleNotFoundError:
                pass

        model_dict = {}
        for model in self.model_list:
            skip_field_list = ['id', 'created_at', 'updated_at']
            update_field_type_list = ['CharField', 'ForeignKey', 'TextField']
            model_dict[model] = {
                'fill_optional': sorted([i.name for i in model._meta.fields if i.blank is True and i.null is False and
                                         i.unique is not True and i.name not in skip_field_list]),
                'update_field_list': sorted([i for i in model._meta.fields if i.get_internal_type() in
                                             update_field_type_list and not i.name.endswith('_id') and
                                             i.name not in skip_field_list], key=lambda x: x.name),
                'create_fk_list': sorted([i.name for i in model._meta.fields if i.get_internal_type() == 'ForeignKey'
                                          and i.null is False and not i._get_default()]),
            }
            if model in auditlog_models:
                model_dict[model]['auditlog'] = True

        data = dict(model_dict=model_dict)

        with open(template_file) as f:
            template = Template(f.read())
        file_text = template.render(data)

        with open(output_path, 'w') as f:
            f.write(file_text)
        self.stdout.write(self.style.SUCCESS(f"{output_path} generated!"))
