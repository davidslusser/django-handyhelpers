"""
Description:
"""

# system modules

# django modules
from django.db import models
from django.db.utils import IntegrityError

# model managers
from handyhelpers.managers import HandyHelperModelManager


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


class SingletonModel(models.Model):
    """ Singleton model to restrict a database table to one row. """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        try:
            self.pk = 1
            super(SingletonModel, self).save(*args, **kwargs)
        except IntegrityError:
            pass

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
