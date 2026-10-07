from django import forms

from .mixins.form_mixins import HtmxFormMixin, SetRequiredMixin


class SetRequiredModelForm(SetRequiredMixin, forms.ModelForm):
    """ModelForm with ``Meta.required`` and ``Meta.not_required`` field lists.

    Fields in both lists are required. Original Django widgets are preserved.
    """


class TimestampFilter(forms.Form):
    """Generic Form class to filter by created_at and updated_at timestamps"""

    created_at__gte = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        required=False,
        label="Created After",
    )
    created_at__lte = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        required=False,
        label="Created Before",
    )
    updated_at__gte = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        required=False,
        label="Updated After",
    )
    updated_at__lte = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        required=False,
        label="Updated Before",
    )


class HtmxModelForm(HtmxFormMixin, forms.ModelForm):
    """ModelForm class with the HtmxFormMixin included"""


class HtmxForm(HtmxFormMixin, forms.Form):
    """Form class with the HtmxFormMixin included"""
