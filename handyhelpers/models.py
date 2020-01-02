"""
Description:
"""

# system modules

# django modules
from django.db import models

# model managers
from djangohelpers.managers import HandyHelperModelManager


class HandyHelperBaseModel(models.Model):
    """ abstract model for common fields in models (these fields will appear in all models) """
    objects = HandyHelperModelManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update(self, **kwargs):
        """ perform an 'update like' operation on a single model instance """
        for i in kwargs:
            setattr(self, i, kwargs[i])
        self.save()

    class Meta:
        abstract = True
