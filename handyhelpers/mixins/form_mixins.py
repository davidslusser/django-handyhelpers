from django import forms
from django.template.loader import get_template


class SetRequiredMixin:
    """ mixin class that sets form fields as required or not_required based on the form Meta class parameters
     'required' and/or 'not_required'. Both parameters are a list of fields in the form. The 'required' parameter takes
     precedence over 'not_required' parameter if fields are listed in both lists.

    example:

        class MyModelForm(SetRequiredMixin, forms.ModelForm):

            class Meta:
                model = MyModel
                widgets = {
                    'some_field': forms.TextInput(attrs={'class': 'form-control'}),
                    'some_other_field': forms.TextInput(attrs={'class': 'form-control'}),
                }
                required = ['some_field']
                not_required = ['some_other_field']
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if getattr(self.Meta, 'not_required', None):
            for field in self.Meta.not_required:
                self.fields[field].required = False

        if getattr(self.Meta, 'required', None):
            for field in self.Meta.required:
                self.fields[field].required = True


class HtmxFormMixin:
    """ mixin class for rendering a Bootstrap 5 form intended to be used with a HTMX view.
    Usage Example:
    
    from handyhelpers.forms import HtmxModelForm
    
    class ContactRequestForm(HtmxModelForm):
        hx_post = "/contact_request"
        hx_target = "contact-request-form"
        success_message = "Contact request received; we'll be in touch soon!"
        
        class Meta:
            model = ContactRequest
            fields = ["name", "email", "phone_number", "message"]

            labels = {
                "name": "Full Name",
                "email": "Email Address",
                "phone_number": "Phone Number",
                "message": "Your Message",
            }   
    """
    hx_post = None
    hx_target = None
    hx_trigger = "submit"
    hx_swap = "innerHTML"
    success_message = None
    use_alert_for_success_message = False
    template_name = "handyhelpers/htmx/bs5/form/inline_form.htm"
    template_disabled_name = "handyhelpers/htmx/bs5/form/inline_form_disabled.htm"
    align = "start" # can be 'start', 'end', 'center'
    disable_on_success = True

    def as_bs5(self):      
        template = get_template(self.template_name)
        context = {
            "hx_post": self.hx_post,
            "hx_trigger": self.hx_trigger,
            "hx_target": self.hx_target,
            "hx_swap": self.hx_swap,
        }
        context["form"] = self
        rendered_html = template.render(context)
        return rendered_html
    
    def as_bs5_disabled(self):      
        template = get_template(self.template_disabled_name)
        context = {
            "hx_post": self.hx_post,
            "hx_trigger": self.hx_trigger,
            "hx_target": self.hx_target,
            "hx_swap": self.hx_swap,
            "disable": True,
        }
        context["form"] = self
        rendered_html = template.render(context)
        return rendered_html
    