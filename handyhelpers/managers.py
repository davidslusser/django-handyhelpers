"""
DESCRIPTION:
    class definitions for common model managers
"""

# system modules
import logging
from simplecrypt import encrypt, decrypt
from random import randint

# django models
from django.db import models
from django.conf import settings


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


class ParentModelMixin(object):
    """ methods for parent models """

    def get_child_list(self):
        """ return a list of child objects """
        return [f.get_accessor_name() for f in self._meta.get_fields()
                if getattr(f, 'field_name', None) and f.one_to_one]

    def get_child(self):
        """ return the child inherited from this parent object instance """
        for i in self.get_child_list():
            child = getattr(self, i, None)
            if child:
                return child
        return None

    def get_grandchild(self):
        """ return the grandchild inherited from this parent object instance """
        child = self.get_child()
        if child:
            return child.get_child()
        return None


class ExcryptionModelMixin(object):
    """ methods for handling encrypted fields """

    @staticmethod
    def decrypt_field(item):
        """ decrypt an encrypted string """
        try:
            return decrypt(settings.SECRET_KEY, item.decode('base64'))
        except Exception as err:
            logging.error(str(err))

    @staticmethod
    def encrypt_field(item):
        """ encrypt a string """
        try:
            return encrypt(settings.SECRET_KEY, item).encode('base64')
        except Exception as err:
            logging.error(str(err))