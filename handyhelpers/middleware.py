from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect


class RequireLoginMiddleware:
    """Middleware used to enforce user login to view page. Redirects to LOGIN_URL as defined in settings if path
    is not in REQUIRED_LOGIN_IGNORE_PATHS"""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        default_ignore_paths = [
            "/accounts/login/",
            "/accounts/logout/",
            "/admin/",
            "/admin/login/",
        ]

        response = self.get_response(request)
        for path in getattr(
            settings, "REQUIRED_LOGIN_IGNORE_PATHS", default_ignore_paths
        ):
            if path in request.path:
                return response

        if not request.user.is_authenticated:
            redirect_url = getattr(
                settings, "LOGIN_URL", request.META.get("HTTP_REFERER")
            )
            content_type = getattr(request, "headers", None).get("Content-Type", None)
            if content_type in ["application/json"]:
                return JsonResponse(
                    {"detail": "Authentication credentials were not provided."}
                )
            return redirect(redirect_url)

        return response
