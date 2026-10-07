"""Bootstrap styling layered onto bound Django fields."""

from django import forms, template

register = template.Library()


@register.filter
def get_form_errors(form, field_name):
    return ", ".join(form.errors.get(field_name, ()))


@register.filter
def get_field_value(form, field_name):
    return form[field_name].value()


@register.simple_tag
def bootstrap_field(field, disabled=False):
    widget = field.field.widget
    attrs = {}
    if not widget.is_hidden:
        if isinstance(
            widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple)
        ):
            css = "form-check-input" if isinstance(widget, forms.CheckboxInput) else ""
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            css = "form-select"
        else:
            css = "form-control"
        classes = widget.attrs.get("class", "").split()
        for name in (css, "is-invalid" if field.errors else ""):
            if name and name not in classes:
                classes.append(name)
        attrs["class"] = " ".join(classes)
    if disabled:
        attrs["disabled"] = True
    return field.as_widget(attrs=attrs)
