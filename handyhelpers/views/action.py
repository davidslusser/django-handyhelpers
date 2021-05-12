"""
This file contains view that perform an action and are redirected to another URL. These view do not render a template.
"""

from django.shortcuts import redirect
from django.views.generic import (View)


class FilterListView(View):
    """ apply filters, as provided via queryparameters, to a list view that uses the FilterByQueryParamsMixin """
    def post(self, request, *args, **kwargs):
        """ process POST request """
        redirect_url = self.request.META.get('HTTP_REFERER')
        form_parameters = self.request.POST.dict()

        # remove csrf token from POST parameters
        if form_parameters.get('csrfmiddlewaretoken'):
            form_parameters.pop('csrfmiddlewaretoken')

        # build filtered URL
        filter_url = f'''{redirect_url.split('?')[0]}?'''
        for key, value in form_parameters.items():
            if value:
                filter_url += f'{key}={value}&'

        return redirect(filter_url)


class ShowAllListView(View):
    """ show all records (undo a FilterListView) """
    def get(self, request, *args, **kwargs):
        """ process GET request """
        redirect_url = self.request.META.get('HTTP_REFERER')
        return redirect(redirect_url.split('?')[0])
