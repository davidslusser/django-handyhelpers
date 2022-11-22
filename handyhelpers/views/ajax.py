import json
import psutil

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
            return HttpResponse(json.dumps({'server_response': template.render({'data': data})}),
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
