"""
Description:
"""

# system modules
import logging
from simplecrypt import encrypt, decrypt

# django modules
from django.db import models
from django.conf import settings

# model managers
from managers import HandyHelperModelManager


class HandyHelperBaseModel(models.Model):
    """ abstract model for common fields in models (these fields will appear in all models) """
    objects = HandyHelperModelManager()
    timestamp = models.DateTimeField(auto_now_add=True)

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

    def update(self, **kwargs):
        """ perform an 'update like' operation on a single model instance """
        for i in kwargs:
            setattr(self, i, kwargs[i])
        self.save()

    class Meta:
        abstract = True
