import json
import psutil

from django.apps import apps
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.http import require_GET, require_POST


@require_GET
def get_host_network_stats(request):
    """
    Description:
        Get network statistics for a given network interface on the host machine.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    if (request.is_ajax()) and (request.method == 'GET'):
        if 'client_response' in request.GET:
            interface = request.GET['client_response']
            data = psutil.net_if_stats()[interface]
            template = loader.get_template('handyhelpers/ajax/host_interface_stats.htm')
            return HttpResponse(json.dumps({'server_response': template.render({'data': data})}),
                                content_type='application/javascript')
        else:
            return HttpResponse('Invalid request inputs', status=400)
    else:
        return HttpResponse('Invalid request', status=400)


@require_GET
def get_host_process_details(request):
    """
    Description:
        Get process details for a given process on the host machine.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    if (request.is_ajax()) and (request.method == 'GET'):
        if 'client_response' in request.GET:
            proc = request.GET['client_response']
            try:
                data = psutil.Process(int(proc))
            except psutil.AccessDenied:
                data = None
            template = loader.get_template('handyhelpers/ajax/host_process_details.htm')
            return HttpResponse(json.dumps({'server_response': template.render({'data': data.as_dict()})}),
                                content_type='application/javascript')
        else:
            return HttpResponse('Invalid request inputs', status=400)
    else:
        return HttpResponse('Invalid request', status=400)


@require_GET
def get_host_partition_usage(request):
    """
    Description:
        Get disk usage for a given partition on the host machine.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    if (request.is_ajax()) and (request.method == 'GET'):
        if 'client_response' in request.GET:
            part = request.GET['client_response']
            try:
                data = psutil.disk_usage(part)
            except psutil.AccessDenied:
                data = None
            template = loader.get_template('handyhelpers/ajax/host_partition_usage.htm')
            return HttpResponse(json.dumps({'server_response': template.render({'data': data})}),
                                content_type='application/javascript')
        else:
            return HttpResponse('Invalid request inputs', status=400)
    else:
        return HttpResponse('Invalid request', status=400)


@require_GET
def get_host_cpu_stats(request):
    """
    Description:
        Get CPU status for a given cpu on the host machine.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    if (request.is_ajax()) and (request.method == 'GET'):
        if 'client_response' in request.GET:
            cpu = int(request.GET['client_response'])
            try:
                data = dict(
                    time=psutil.cpu_times(percpu=True)[cpu],
                    time_percent=psutil.cpu_times_percent(percpu=True)[cpu],
                    frequency=psutil.cpu_freq(percpu=True)[cpu],
                )

            except psutil.AccessDenied:
                data = None
            template = loader.get_template('handyhelpers/ajax/host_cpu_stats.htm')
            return HttpResponse(json.dumps({'server_response': template.render({'data': data})}),
                                content_type='application/javascript')
        else:
            return HttpResponse('Invalid request inputs', status=400)
    else:
        return HttpResponse('Invalid request', status=400)


@require_GET
def get_auditlog_entry_details(request):
    """
    Description:
        Get details for a LogEntry of auditlog.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    if not apps.is_installed('auditlog'):
        return HttpResponse('Invalid request', status=400)
    if (request.is_ajax()) and (request.method == 'GET'):
        LogEntry = apps.get_model('auditlog', 'LogEntry')
        if 'client_response' in request.GET:
            object_id = request.GET['client_response']
            obj = LogEntry.objects.get(id=object_id)
            template = loader.get_template('handyhelpers/ajax/get_auditlog_entry_details.htm')
            return HttpResponse(json.dumps({'server_response': template.render({'object': obj})}),
                                content_type='application/javascript')
        else:
            return HttpResponse('Invalid request inputs', status=400)
    else:
        return HttpResponse('Invalid request', status=400)
