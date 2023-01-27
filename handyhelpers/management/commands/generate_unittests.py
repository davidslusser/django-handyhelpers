from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.urls import URLPattern, URLResolver
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
        self.model_list = self.get_model_list()
        files_created_list = []

        # build model unittests
        if 'model' in options['test_type']:
            self.build_model_unittests(output_path=options['output_path'],
                                       output_file=options['output_file'],
                                       template_file=options['template'])
        elif 'viewset' in options['test_type']:
            self.build_viewset_unittests(output_path=options['output_path'],
                                         output_file=options['output_file'],
                                         template_file=options['template'])
        else:
            print(f'''unittest generation for {options['test_type']} is not currently supported''')

        for item in files_created_list:
            if item:
                self.stdout.write(self.style.SUCCESS(f'generated {item}'))

    @staticmethod
    def my_import(name):
        """ https://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class """
        components = name.split('.')
        mod = __import__(components[0])
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    @staticmethod
    def get_model_field_names(model, exclude_list=()):
        """ return a list of field names for a given model """
        return [i.name for i in model._meta.fields if type(i).__name__ not in exclude_list]

    def get_model_list(self):
        """ return a list of all models in application """
        app = apps.get_app_config(self.app)
        model_list = list(app.get_models())
        model_list.sort(key=lambda x: x.__name__)
        return model_list

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

    def build_viewset_unittests(self, output_path=None, output_file=None, template_file=None):
        """ build unittest file for drf viewsets """
        try:
            if not template_file:
                template_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                             'unittest_templates', 'viewsets.jinja')

            if output_file:
                output_path = output_file
            elif not output_path:
                output_path = 'test_viewsets.py'
            elif os.path.isdir(output_path):
                output_path = f'{output_path}/test_veiwsets.py'

            test_dict = {} # {'view': view_object, url_list: list_of_route_names}
            route_name_list = []
            url_data = __import__(getattr(settings, 'ROOT_URLCONF'), {}, {}, [''])
            app_name = self.app_name if self.app_name else self.app
            app_urls = [i for i in url_data.urlpatterns if hasattr(i, 'app_name') and i.app_name == app_name]
            for path in app_urls:
                for item in path.url_patterns:
                    if isinstance(item, URLResolver):
                        for route in item.url_patterns:
                            if route.name in ['api-root']:
                                continue
                            v = self.my_import(route.lookup_str)
                            if not hasattr(v, 'model'):
                                self.stdout.write(self.style.WARNING(f'INFO: can not find model in the viewset for '
                                                                     f'{route.name}; skipping unittest generation'))
                                continue
                            if not hasattr(route, 'app_name'):
                                route.app_name = path.app_name
                            if v in test_dict:
                                if route not in test_dict[v]:
                                    if route.name not in route_name_list:
                                        test_dict[v].append(route)
                                        route_name_list.append(route.name)
                            else:
                                if route.name not in route_name_list:
                                    test_dict[v] = [route]
                                    route_name_list.append(route.name)

            data = dict(data=test_dict)
            with open(template_file) as f:
                template = Template(f.read())
            file_text = template.render(data)
            with open(output_path, 'w') as f:
                f.write(file_text)
            return output_path

        except Exception as err:
            self.stdout.write(self.style.ERROR(f'error generating viewset unittests: {err}'))


    def build_view_unittests(self, output_path=None, output_file=None, template_file=None):
        """ build unittest file for views """
        if not template_file:
            template_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         'unittest_templates', 'viewsets.jinja')

        if output_file:
            output_path = output_file
        elif not output_path:
            output_path = 'test_viewsets.py'
        elif os.path.isdir(output_path):
            output_path = f'{output_path}/test_veiwsets.py'

        app_url_list = []
        url_data = __import__(getattr(settings, 'ROOT_URLCONF'), {}, {}, [''])
        app_urls = [i for i in url_data.urlpatterns if hasattr(i, 'app_name') and i.app_name == self.app]
        for path in app_urls:
            for item in path.url_patterns:
                if isinstance(item, URLPattern):
                    if item in app_url_list:
                        continue
                    app_url_list.append(item)
                    print(item.name, item.lookup_str, item.pattern)
