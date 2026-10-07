from django import forms
from django.shortcuts import render

from handyhelpers.forms import HtmxModelForm
from handyhelpers.views.htmx import CreateModelModalView, HtmxPostForm
from tests.models import Item


class BrowserForm(HtmxModelForm):
    upload = forms.FileField(required=False)
    hx_post = "/browser/form/"
    hx_target = "inline-form"
    submit_button_text = "Save inline"
    success_message = "Saved inline"

    class Meta:
        model = Item
        fields = ["name", "number", "upload"]

    def save(self, *args, **kwargs):
        obj = super().save(*args, **kwargs)
        upload = self.cleaned_data.get("upload")
        if upload:
            obj.name = f"{obj.name} ({upload.size} bytes)"
            obj.save()
        return obj


class Modal(CreateModelModalView):
    form = BrowserForm


class Inline(HtmxPostForm):
    form = BrowserForm


def page(request):
    return render(
        request,
        "browser.htm",
        {
            "form": BrowserForm(),
            "chart": {"id": "example-chart", "label_list": ["A", "B"], "value_list": [1, 2]},
            "rows": range(25),
        },
    )


def partial(request):
    return render(request, "browser_partial.htm", {"rows": range(25)})
