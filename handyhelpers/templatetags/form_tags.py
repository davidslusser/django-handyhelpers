from django import template

register = template.Library()


@register.filter
def get_form_errors(form, field_name):
    """Get errors on a form field

    Args:
        form (Form): django form object
        field_name (str): name of form field

    Returns:
        str: comma separated list of errors on the form field

    Usage Example:
        {{ form|get_form_errors:field.name }}
    """
    try:
        error_list = [
            item for sublist in form.errors.as_data()[field_name] for item in sublist
        ]
        return ", ".join(error_list)
    except Exception:
        return ""


@register.filter
def get_field_value(form, field_name):
    """Get the value of a form field

    Args:
        form (Form): django form object
        field_name (str): name of form field

    Returns:
        str: value of the form field

    Usage Example:
        {{ form|get_field_value:field.name }}
    """

    try:
        return form.data.get(field_name)
    except Exception:
        return ""
