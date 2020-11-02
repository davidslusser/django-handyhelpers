from django.urls import path
from handyhelpers.views import action

app_name = 'handyhelpers'

urlpatterns = [
    # action views
    path('filter_list_view', action.FilterListView.as_view(), name='filter_list_view'),
    path('show_all_list_view', action.ShowAllListView.as_view(), name='show_all_list_view'),
]
