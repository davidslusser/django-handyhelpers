from django.urls import path
from handyhelpers.views import action
from handyhelpers.views import ajax
from handyhelpers.views import host
from handyhelpers.views import htmx

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
    path('host_interface_stats', ajax.get_host_network_stats, name='host_interface_stats'),
    path('host_process_details', ajax.get_host_process_details, name='host_process_details'),
    path('host_partition_usage', ajax.get_host_partition_usage, name='host_partition_usage'),
    path('get_host_cpu_stats', ajax.get_host_cpu_stats, name='get_host_cpu_stats'),
    path('get_auditlog_entry_details', ajax.get_auditlog_entry_details, name='get_auditlog_entry_details'),

    # htmx views
    path('get_host_processes/', htmx.GetHostProcesses.as_view(), name='get_host_processes'),

]
