import psutil
from django.shortcuts import render
from django.views.generic import (View)

# import forms
from handyhelpers.forms import HostProcessFilterForm


class GetHostProcesses(View):
    def get(self, request):
        context = dict()
        process_list = list(psutil.process_iter())
        filtered_process_list = list()
        filter_form = HostProcessFilterForm(request.GET or None)

        # check for form clearing
        if request.GET.dict().get('clear', None):
            context['clear_filter'] = False

        else:
            if filter_form.is_valid():
                context['clear_filter'] = True
                if filter_form.cleaned_data['status']:
                    for i in process_list:
                        try:
                            if i.status() in filter_form.cleaned_data['status']:
                                filtered_process_list.append(i)
                        except psutil.NoSuchProcess:
                            continue
                    process_list = filtered_process_list

                if filter_form.cleaned_data.get('created_at__gte', None):
                    for i in process_list:
                        try:
                            if i.create_time() > filter_form.cleaned_data['created_at__gte'].timestamp():
                                filtered_process_list.append(i)
                        except psutil.NoSuchProcess:
                            continue
                        process_list = filtered_process_list
                if filter_form.cleaned_data.get('created_at__lte', None):
                    for i in process_list:
                        try:
                            if i.create_time() < filter_form.cleaned_data['created_at__lte'].timestamp():
                                filtered_process_list.append(i)
                        except psutil.NoSuchProcess:
                            continue
                        process_list = filtered_process_list

        context['process_list'] = process_list
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
        return render(request, template_name='handyhelpers/snippets/host_process_card.htm', context=context)
