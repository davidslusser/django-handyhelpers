from django.conf import settings
from django.shortcuts import redirect


class RequireLoginMiddleware:
    """ Middleware used to enforce user login to view page. Redirects to LOGIN_URL as defined in settings if path
     is not in REQUIRED_LOGIN_IGNORE_PATHS """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        default_ignore_paths = [
            '/accounts/login/',
            '/accounts/logout/',
            '/admin/',
            '/admin/login/',
        ]
        response = self.get_response(request)
        if request.path in getattr(settings, 'REQUIRED_LOGIN_IGNORE_PATHS', default_ignore_paths):
            return response

        if not request.user.is_authenticated:
            redirect_url = getattr(settings, 'LOGIN_URL', request.META.get('HTTP_REFERER'))
            return redirect(redirect_url)

        return response
