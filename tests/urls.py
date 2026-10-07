from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView

from tests import browser_app

urlpatterns = [
    path("handyhelpers/", include("handyhelpers.urls")),
    path(
        "",
        TemplateView.as_view(template_name="handyhelpers/handyhelpers_base_bs5.htm"),
        name="home",
    ),
    path("items/", lambda request: HttpResponse("items"), name="items"),
    path(
        "calendar/<int:year>/<int:month>/",
        lambda request, **kwargs: HttpResponse("calendar"),
        name="calendar",
    ),
]


urlpatterns += [
    path("browser/", browser_app.page, name="browser"),
    path("browser/modal/", browser_app.Modal.as_view()),
    path("browser/form/", browser_app.Inline.as_view()),
    path("browser/partial/", browser_app.partial),
]
urlpatterns += staticfiles_urlpatterns()
