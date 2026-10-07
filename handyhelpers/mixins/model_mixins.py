from django.core.exceptions import ValidationError
from django.db import models


class NonEmptyStringMixin:
    """Mixin for adding non-empty validation to CharFields with blank=False"""

    def get_non_blank_char_fields(self):
        # Retrieve all fields of the model

        # Filter the fields based on type and blank attribute
        return [
            i for i in self._meta.get_fields() if isinstance(i, models.CharField) and not i.blank
        ]

    def clean(self):
        non_blank_char_fields = self.get_non_blank_char_fields()
        for field in non_blank_char_fields:
            if not getattr(self, field.name):
                raise ValidationError(f"The {field.name} field cannot be empty.")
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
