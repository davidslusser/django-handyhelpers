from django.template import loader
from auditlog.models import LogEntry

from .ajax import AjaxGetView

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
