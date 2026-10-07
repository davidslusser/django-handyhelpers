from django.core.exceptions import ValidationError as DjangoValidationError

from handyhelpers.mixins.serializer_mixins import FlexFieldsMixin
from handyhelpers.utils import optional_import

serializers = optional_import("rest_framework.serializers", "api")


class FkReadWriteField(serializers.RelatedField):
    """A generic serializer field that provides the string representation of a ForeignKey object, as provided
    by the __str__ model method, for a read operation, and performs a lookup using the provided lookup_field for
    write operations.

    Example usage:
        my_fk_field = FkReadWriteField(required=False, queryset=MyModel.objects.all(), lookup_field='fk_field_name')
    """

    def __init__(self, **kwargs):
        self.model = kwargs["queryset"].model
        self.lookup_field = kwargs.pop("lookup_field", None)
        if not self.lookup_field:
            self.lookup_field = self.model._meta.pk.name
        super().__init__(**kwargs)

    @staticmethod
    def to_representation(data):
        return str(data)

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.lookup_field: data})
        except self.model.DoesNotExist:
            raise serializers.ValidationError(
                f"{self.model._meta.model_name} with {self.lookup_field} '{data}' not found"
            )
        except self.model.MultipleObjectsReturned:
            raise serializers.ValidationError(
                "multiple objects returned; lookup_field must be unique"
            )
        except (TypeError, ValueError, DjangoValidationError) as error:
            raise serializers.ValidationError("Invalid related-object lookup value") from error


class NoModelFlexSerializer(FlexFieldsMixin, serializers.Serializer):
    """A serializer that provides dynamical filtering of fields in the return data.

    Example usage:
        class ExampleViewSet(viewsets.ViewSet):
            def list(self, request):
                data = {}
                serializer = NoModelSerializer(data, context={"request": request})
                return Response(serializer.data)
    """

    pass
