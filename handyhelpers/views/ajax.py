import json
import psutil

from django.views import View
from django.apps import apps
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.http import require_GET

from auditlog.models import LogEntry


class AjaxGetView(View):
    """ generic view for handling GET requests sent via ajax """
    template = None
    data = {}

    def get(self, request, *args, **kwargs):
        try:
            if not self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return HttpResponse('Invalid request', status=400)    
            if 'client_response' in self.request.GET:
                return HttpResponse(json.dumps({'server_response': self.template.render({'data': self.data})}),
                                    content_type='application/javascript')
            return HttpResponse('Invalid request inputs', status=400)
        except Exception:
            return HttpResponse(json.dumps({'server_response': self.template.render({'data': None})}),
                                    content_type='application/javascript')


class GetAuditLogEntries(AjaxGetView):
    """
    Description:
        Get AuditLog entries for a given model and instance.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    template = loader.get_template('handyhelpers/ajax/get_auditlog_entries.htm')
    
    def get(self, request, *args, **kwargs):
        self.data = LogEntry.objects.filter(content_type__model=kwargs['model_name'], 
                                       object_pk=kwargs['pk'])
        return super().get(request, *args, **kwargs)


class GetAuditLogEntry(AjaxGetView):
    """
    Description:
        Get details for a LogEntry of auditlog..
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    template = loader.get_template('handyhelpers/ajax/get_auditlog_entry.htm')
    
    def get(self, request, *args, **kwargs):
        self.data = LogEntry.objects.filter(id=kwargs['id'])
        return super().get(request, *args, **kwargs)


       
class GetHostNetworkStats(AjaxGetView):
    """
    Description:
        Get network statistics for a given network interface on the host machine.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    template = loader.get_template('handyhelpers/ajax/host_interface_stats.htm')
    
    def get(self, request, *args, **kwargs):
        interface = self.request.GET['client_response']
        self.data = psutil.net_if_stats()[interface]
        return super().get(request, *args, **kwargs)


class GetHostProcessDetails(AjaxGetView):
    """
    Description:
        Get process details for a given process on the host machine.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    template = loader.get_template('handyhelpers/ajax/host_process_details.htm')
    
    def get(self, request, *args, **kwargs):
        proc = request.GET['client_response']
        try:
            self.data = psutil.Process(int(proc))
        except psutil.AccessDenied:
            self.data = {}
        return super().get(request, *args, **kwargs)
    
    
class GetHostParitionUsage(AjaxGetView):
    """
    Description:
        Get disk usage for a given partition on the host machine.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    template = loader.get_template('handyhelpers/ajax/host_partition_usage.htm')
    
    def get(self, request, *args, **kwargs):
        part = request.GET['client_response']
        self.data = psutil.disk_usage(part)
        return super().get(request, *args, **kwargs)


class GetHostCpuStats(AjaxGetView):
    """
    Description:
        Get CPU status for a given cpu on the host machine.
    Args:
        request: AJAX request object.
    Returns:
        HttpResponse: JSON formatted response.
    """
    template = loader.get_template('handyhelpers/ajax/host_cpu_stats.htm')
    
    def get(self, request, *args, **kwargs):
        cpu = int(request.GET['client_response'])
        self.data = dict(
            time=psutil.cpu_times(percpu=True)[cpu],
            time_percent=psutil.cpu_times_percent(percpu=True)[cpu],
            frequency=psutil.cpu_freq(percpu=True)[cpu],
        )
        return super().get(request, *args, **kwargs)
