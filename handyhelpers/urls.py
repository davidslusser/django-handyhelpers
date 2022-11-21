from django.urls import path
from handyhelpers.views import action
from handyhelpers.views import ajax
from handyhelpers.views import host

app_name = 'handyhelpers'

urlpatterns = [
    # host views
    path('host_details/', host.ShowHost.as_view(), name='host_details'),
    path('host_network/', host.ShowHostNetwork.as_view(), name='host_network'),
    path('host_process/', host.ShowHostProcesses.as_view(), name='host_process'),

    # action views
    path('filter_list_view', action.FilterListView.as_view(), name='filter_list_view'),
    path('show_all_list_view', action.ShowAllListView.as_view(), name='show_all_list_view'),

    # ajax views
    path('host_interface_stats', ajax.get_host_network_stats, name='host_interface_stats'),
    path('host_process_details', ajax.get_host_process_details, name='host_process_details'),

]
