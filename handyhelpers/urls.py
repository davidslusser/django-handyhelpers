from django.conf import settings
from django.urls import path
from handyhelpers.views import action
from handyhelpers.views import host
from handyhelpers.views import htmx

if 'auditlog' in settings.INSTALLED_APPS:
    from handyhelpers.views import auditlog
    

app_name = 'handyhelpers'

urlpatterns = [
    # host views
    path('host_details/', host.ShowHost.as_view(), name='host_details'),
    path('host_network/', host.ShowHostNetwork.as_view(), name='host_network'),
    path('host_process/', host.ShowHostProcesses.as_view(), name='host_process'),
    path('host_disk/', host.ShowHostDisk.as_view(), name='host_disk'),
    path('host_memory/', host.ShowHostMemory.as_view(), name='host_memory'),
    path('host_cpu/', host.ShowHostCpu.as_view(), name='host_cpu'),

    # action views
    path('filter_list_view', action.FilterListView.as_view(), name='filter_list_view'),
    path('show_all_list_view', action.ShowAllListView.as_view(), name='show_all_list_view'),

    # ajax views
    path('host_interface_stats/', host.GetHostNetworkStats.as_view(), name='host_interface_stats'),
    path('host_process_details/', host.GetHostProcessDetails.as_view(), name='host_process_details'),
    path('host_partition_usage/', host.GetHostParitionUsage.as_view(), name='host_partition_usage'),
    path('get_host_cpu_stats/', host.GetHostCpuStats.as_view(), name='get_host_cpu_stats'),

    # htmx views
    path('get_host_processes/', htmx.GetHostProcesses.as_view(), name='get_host_processes'),

]

if 'auditlog' in settings.INSTALLED_APPS:
    urlpatterns.extend(
        [
            path('get_auditlog_entries/<str:model_name>/<str:pk>/', auditlog.GetAuditLogEntries.as_view(), name='get_auditlog_entries'),
            path('get_auditlog_entry/<int:id>/', auditlog.GetAuditLogEntry.as_view(), name='get_auditlog_entry'),
        ]
    )
