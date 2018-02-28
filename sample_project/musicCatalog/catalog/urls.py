from django.conf.urls import url
from catalog import views


urlpatterns = [
    # custom views
    url(r'^$', views.CatalogHomeView.as_view(), name='catalog_home'),
    url(r'^home$', views.CatalogHomeView.as_view(), name='catalog_home'),

    # list views
    # url(r'^list_tasks_all/$', views.ListTasks.as_view(), name='list_tasks_all'),

    # detail views
    # url(r'^show_results_by_day/$', views.RallyResultsByDay.as_view(), name='show_results_by_day'),

    # csv export views
    url(r'^csv_artists/$', views.ArtistCsvView.as_view(), name='csv_artists'),

    # ajax views
    # url(r'^get_rally_subtasks', ajax.get_subtasks, name='get_rally_subtasks'),

]
