import os
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from handyhelpers.utils import optional_import

__version__ = "0.0.3"


class Command(BaseCommand):
    help = "Create admin.py file, based on a jinja2 template, for a given app"

    def __init__(self):
        self.opts = None
        self.app = None
        self.model_list = None
        super().__init__()

    def add_arguments(self, parser):
        """define command arguments"""
        parser.add_argument(
            "--force", action="store_true", help="Overwrite an existing output file"
        )
        parser.add_argument("app", type=str, help="name of the django app")
        parser.add_argument(
            "--template",
            type=str,
            help="path to Jinja template used to create admin.py file",
        )
        parser.add_argument("--output_file", type=str, help="path of output file to create")

    def handle(self, *args, **options):
        """command entry point"""
        try:
            self.app_config = apps.get_app_config(options["app"])
        except LookupError:
            self.app_config = next(
                (
                    config
                    for config in apps.get_app_configs()
                    if config.name == options["app"]
                    or f"{config.__class__.__module__}.{config.__class__.__name__}"
                    == options["app"]
                ),
                None,
            )
            if self.app_config is None:
                raise CommandError(f"{options['app']} is not an installed application")

        self.opts = options
        self.app = options["app"]
        self.get_model_list()
        self.get_admin_template()
        self.get_output_file()
        self.build_admin()
        self.stdout.write(self.style.SUCCESS(f"{self.opts['output_file']} created!"))

    def get_output_file(self):
        """return the full path of the created file"""
        if not self.opts["output_file"]:
            self.opts["output_file"] = str(Path(self.app_config.path) / "admin.py")

    def get_admin_template(self):
        """return the full path of the jinja template to use in creating the admin.py file"""
        if not self.opts["template"]:
            self.opts["template"] = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "admin_templates",
                "admin.jinja",
            )

    def get_model_list(self):
        """return a list of all models in application"""
        app = self.app_config
        self.model_list = list(app.get_models())

    @staticmethod
    def get_model_field_names(model, exclude_list=()):
        """return a list of field names for a given model"""
        return [i.name for i in model._meta.fields if type(i).__name__ not in exclude_list]

    def build_admin(self):
        """build the admin.py file"""
        model_fields = {}
        for model in self.model_list:
            model_fields[model.__name__] = self.get_model_field_names(model)

        data = {
            "model_list": self.model_list,
            "app_name": self.app_config.name,
            "models_file": "models",
            "model_data": self.get_models_and_fields(),
        }

        with open(self.opts["template"], encoding="utf-8") as f:
            template = optional_import("jinja2", "admin").Template(f.read())
        file_text = template.render(data)

        output = Path(self.opts["output_file"])
        mode = "w" if self.opts["force"] else "x"
        try:
            with output.open(mode, encoding="utf-8") as f:
                f.write(file_text)
        except FileExistsError as error:
            raise CommandError(f"{output} exists; use --force to overwrite it") from error

    @staticmethod
    def get_display_fields(model, exclude_field_list=()):
        """build and return a list of 'list_display' to be used in admin.py for a given model"""
        display_field_list = []
        display_field_list.append(model._meta.pk.name)
        for i in model._meta.fields:
            if i.get_internal_type() not in exclude_field_list and i.name not in display_field_list:
                display_field_list.append(i.name)
        return display_field_list

    @staticmethod
    def get_search_fields(
        model,
        exclude_field_list=("AutoField", "BooleanField", "DateTimeField", "ForeignKey"),
    ):
        """build and return a list of 'search_fields' to be used in admin.py for a given model"""
        return [
            i.name for i in model._meta.fields if i.get_internal_type() not in exclude_field_list
        ]

    @staticmethod
    def get_filter_fields(model, include_field_list=("BooleanField", "ForeignKey", "CharField")):
        """build and return a list of 'filter_fields' to be used in admin.py for a given model"""
        return_list = []
        for i in model._meta.fields:
            field_type = i.get_internal_type()
            if field_type in include_field_list:
                if field_type == "CharField" and not i.choices:
                    continue
                elif field_type == "CharField" and i.choices:
                    return_list.append(i.name)
                else:
                    return_list.append(i.name)
        return return_list

    def get_models_and_fields(self):
        return_data = {}
        for model in self.model_list:
            return_data[model.__name__] = {
                "display_fields": self.get_display_fields(model),
                "search_fields": self.get_search_fields(model),
                "filter_fields": self.get_filter_fields(model),
            }
        return return_data
