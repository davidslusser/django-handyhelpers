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


class TimestampFilter(forms.Form):
    """ Generic Form class to filter by created_at and updated_at timestamps """
    created_at__gte = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                                      required=False, label='Created After')
    created_at__lte = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                                      required=False, label='Created Before')
    updated_at__gte = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                                      required=False, label='Updated After')
    updated_at__lte = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                                      required=False, label='Updated Before')
