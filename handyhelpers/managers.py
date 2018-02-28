"""
DESCRIPTION:
    class definitions for common model managers
"""

# system modules
from random import randint

# django models
from django.db import models


class HandyHelperModelManager(models.Manager):
    def get_object_or_none(self, **kwargs):
        """ return object if available; return None if not available """
        try:
            return super(HandyHelperModelManager, self).get(**kwargs)
        except models.ObjectDoesNotExist:
            return None

    def filter_or_none(self, **kwargs):
        """ return object if available; return None if not available """
        try:
            return super(HandyHelperModelManager, self).filter(**kwargs)
        except models.ObjectDoesNotExist:
            return None

    def get_latest_or_none(self, *args, **kwargs):
        """ return latest object id available; None if not available """
        try:
            return super(HandyHelperModelManager, self).latest(*args, **kwargs)
        except models.ObjectDoesNotExist:
            return None

    def get_fields(self, exclude_list=('OneToOneField')):
        """ return a list of fields in the model """
        if not issubclass(self.model, models.Model):
            return []
        return [i for i in self.model._meta.fields if type(i).__name__ not in exclude_list]

    def get_field_names(self, exclude_list=('OneToOneField')):
        """ return a list of field names in the model """
        if not issubclass(self.model, models.Model):
            return []
        return [i.name for i in self.model._meta.fields if type(i).__name__ not in exclude_list]

    def get_properties(self):
        """ return a list of model property names """
        if not issubclass(self.model, models.Model):
            return []
        properties_list = []
        for name in dir(self.model):
            if isinstance(getattr(self.model, name), property):
                properties_list.append(name)
        return properties_list

    def get_fields_and_properties(self):
        """ return a list of fields and properties in a model """
        return self.get_fields() + self.get_properties()

    def get_foreign_keys(self):
        """ return a list of foreignKeys in the model """
        if not issubclass(self.model, models.Model):
            return []
        return [i for i in self.model._meta.fields if i.get_internal_type() == "ForeignKey"]

    def get_foreign_key_names(self):
        """ return a list of names of foreignKeyfields """
        return [i.name for i in self.get_foreign_keys()]

    def get_random_row(self, **kwargs):
        """ return a single, random entry from a queryset """
        queryset = self.filter(**kwargs)
        if queryset:
            random_index = randint(0, queryset.count() - 1)
            return queryset[random_index]
        return None
