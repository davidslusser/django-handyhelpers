from django import forms

from .mixins.form_mixins import SetRequiredMixin


class SetRequiredModelForm(SetRequiredMixin, forms.ModelForm):
    """
    A form class to add functionality from the SetRequiredMixin to a ModelForm. This allows for form fields specified
    in the 'required' parameter to be required on the rendered form. This further allows for form fields specified
    in the 'not_required' parameter to be not be required on the rendered form. Both the 'required' and 'not_required'
    parameters should be provided as a list or set when used.

        example:

        class MyModelForm(SetRequiredModelForm):

            class Meta:
                model = MyModel
                widgets = {
                    'some_field': forms.TextInput(attrs={'class': 'form-control'}),
                    'some_other_field': forms.TextInput(attrs={'class': 'form-control'}),
                }
                required = ['some_field']
                not_required = ['some_other_field']
    """
