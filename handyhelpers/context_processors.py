from django.conf import settings


def base_template(request):
    return {'BASE_TEMPLATE': getattr(settings, 'BASE_TEMPLATE', 'handyhelpers/handyhelpers_base.htm')}
