"""Form validation and Bootstrap 5 rendering without replacing Django widgets."""

from django.template.loader import get_template


class SetRequiredMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        meta = getattr(self, "Meta", None)
        for name in getattr(meta, "not_required", ()):
            self.fields[name].required = False
        for name in getattr(meta, "required", ()):
            self.fields[name].required = True


class HtmxFormMixin:
    hx_post = hx_target = success_message = None
    hx_trigger = "submit"
    hx_swap = "outerHTML"
    template_name = "handyhelpers/htmx/bs5/form/inline_form.htm"
    template_disabled_name = "handyhelpers/htmx/bs5/form/inline_form_disabled.htm"
    align = "start"
    disable_on_success = True
    use_alert_for_success_message = False
    submit_button_text = "Submit"

    def as_bs5(self):
        return get_template(self.template_name).render({"form": self})

    def as_bs5_disabled(self):
        return get_template(self.template_disabled_name).render({"form": self, "disable": True})
