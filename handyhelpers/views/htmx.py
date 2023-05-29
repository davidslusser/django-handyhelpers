import datetime
import psutil

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.views.generic import View


# import forms
from handyhelpers.forms import HostProcessFilterForm


class GetHostProcesses(View):
    def get(self, request):
        context = dict()
        process_list = list(psutil.process_iter())
        filter_form = HostProcessFilterForm(request.GET or None)

        counts = dict(
            running=len([i for i in process_list if i.status() == 'running']),
            sleeping=len([i for i in process_list if i.status() == 'sleeping']),
            idle=len([i for i in process_list if i.status() == 'idle']),
            stopped=len([i for i in process_list if i.status() == 'stopped']),
            zombie=len([i for i in process_list if i.status() == 'zombie']),
            dead=len([i for i in process_list if i.status() == 'dead']),
        )
        context['counts'] = counts

        # check for form clearing
        if request.GET.dict().get('clear', None):
            context['clear_filter'] = False

        else:
            if filter_form.is_valid():
                context['clear_filter'] = True
                if filter_form.cleaned_data.get('status', None):
                    filtered_process_list = list()
                    for i in process_list:
                        try:
                            if i.status() in filter_form.cleaned_data['status']:
                                filtered_process_list.append(i)
                        except psutil.NoSuchProcess:
                            continue
                    process_list = filtered_process_list

                if filter_form.cleaned_data.get('created_at__gte', None):
                    filtered_process_list = list()
                    for i in process_list:
                        try:
                            if i.create_time() > filter_form.cleaned_data['created_at__gte'].timestamp():
                                filtered_process_list.append(i)
                        except psutil.NoSuchProcess:
                            continue
                    process_list = filtered_process_list
                if filter_form.cleaned_data.get('created_at__lte', None):
                    filtered_process_list = list()
                    for i in process_list:
                        try:
                            if i.create_time() < filter_form.cleaned_data['created_at__lte'].timestamp():
                                filtered_process_list.append(i)
                        except psutil.NoSuchProcess:
                            continue
                    process_list = filtered_process_list
        context['process_list'] = process_list
        context['title'] = 'Host Processes'
        context['now'] = datetime.datetime.now()
        context['subtitle'] = psutil.os.uname()[1]
        filter_form = dict()
        filter_form['form'] = HostProcessFilterForm(request.GET or None)
        filter_form['modal_name'] = 'filter_processes'
        filter_form['modal_size'] = 'modal-lg'
        filter_form['modal_title'] = 'Filter Host Processes'
        filter_form['hx_method'] = 'hx-get'
        filter_form['hx_url'] = '/handyhelpers/get_host_processes'
        filter_form['hx_target'] = 'id_process_list_container'
        filter_form['method'] = 'GET'
        filter_form['action'] = 'Filter'
        context['filter_form'] = filter_form
        return render(request, template_name='handyhelpers/snippets/host_process_card_swap.htm', context=context)


class GenericHtmxView(View):
    """ Generic view for handling HTMX requests; intended to be used with snippets/partials.
    
    context       - context dictionary containing data to be rendered in template
    template_name - template used when rendering page; defaults to: handyhelpers/generic/generic_list.html
    """
    template_name = None
    context = {}
    
    def get(self, request, *args, **kwargs):
        if not self.request.headers.get("Hx-Request", None):
            return HttpResponse("Invalid request", status=400)  
        return render(request, self.template_name, self.context)


class BuildBootstrapModalView(GenericHtmxView):
    """ Generic view used to build a Boostrap 5 modal via HTMX.
    
    class parameters:
        template_name       - template used to render modal; defaults to "handyhelpers/htmx/bs5/modal_swap.htm"
        modal_size          - size of the modal; defaults to "modal-md"
        modal_title         - title used in modal header
        modal_subtitle      - subtitle used in modal header
        modal_body          - contents of modal body
        modal_button_close  - text to use on close button; defaults to "Close"
        modal_button_submit - text to use on submit button; defaults to "Submit"
    """
    template_name = "handyhelpers/htmx/bs5/generic_modal_swap.htm"
    modal_size = "modal-md"
    modal_title = None
    modal_subtitle = None
    modal_body = None
    modal_button_close = "Close"
    modal_button_submit = "Submit"

    def get(self, request, *args, **kwargs):
        if not self.request.headers.get("Hx-Request", None):
            return HttpResponse('Invalid request', status=400)  
        self.context = {
            "modal_header": self.build_model_header(), 
            "modal_body": self.modal_body,
            "modal_size": self.modal_size,
            "modal_button_close": self.modal_button_close,
            "modal_button_submit": self.modal_button_submit,
        }
        return super().get(request, *args, **kwargs)

    def build_model_header(self):
        context = {"modal_title": self.modal_title, "modal_subtitle": self.modal_subtitle}
        return loader.render_to_string("handyhelpers/htmx/bs5/modal_header.htm", context=context)
