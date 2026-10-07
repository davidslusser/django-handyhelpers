from django.contrib.auth.models import AbstractUser
from django.db import models

from handyhelpers.mixins.model_mixins import NonEmptyStringMixin
from handyhelpers.models import HandyHelperBaseModel, SingletonModel


class User(AbstractUser):
    pass


class Category(HandyHelperBaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Item(HandyHelperBaseModel):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    event_at = models.DateTimeField(null=True)
    active = models.BooleanField(default=False)
    number = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/items/" + str(self.pk) + "/"


class Configuration(SingletonModel):
    name = models.CharField(max_length=100, default="Settings")


class RequiredName(NonEmptyStringMixin, models.Model):
    name = models.CharField(max_length=100)
