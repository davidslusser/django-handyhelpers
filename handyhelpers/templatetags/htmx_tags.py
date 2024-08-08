from django import template
from django.urls import reverse
from django.utils.http import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def append_query_params(context, url_name, display=None, **kwargs):
    request = context['request']
    query_params = request.GET.copy()

    for key, value in kwargs.items():
        query_params[key] = value

    if display:
        url = reverse(url_name, kwargs={'display': display})
    else:
        url = reverse(url_name)
    
    query_string = query_params.urlencode()
    return f"{url}?{query_string}" if query_string else url
