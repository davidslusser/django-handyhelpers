from django.conf import settings


def base_template(request):
    return {'BASE_TEMPLATE': getattr(settings, 'BASE_TEMPLATE', 'handyhelpers/handyhelpers_base_bs5.htm')}


def get_settings(request):
    return {'BASE_TEMPLATE': getattr(settings, 'BASE_TEMPLATE', 'handyhelpers/handyhelpers_base_bs5.htm'),
            'PROJECT_NAME': getattr(settings, 'PROJECT_NAME', ''),
            'PROJECT_VERSION': getattr(settings, 'PROJECT_VERSION', ''),
            }
