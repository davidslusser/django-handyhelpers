import datetime
import psutil
from django.shortcuts import render
from django.views.generic import (View)

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
