"""Authentication enforcement before a protected view executes."""

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse


class RequireLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ignored = getattr(
            settings,
            "REQUIRED_LOGIN_IGNORE_PATHS",
            ["/accounts/login/", "/accounts/logout/", "/admin/"],
        )
        exempt = any(
            request.path == path.rstrip("/") or request.path.startswith(path.rstrip("/") + "/")
            for path in ignored
        )
        if not exempt and not request.user.is_authenticated:
            if (
                request.content_type == "application/json"
                or "application/json" in request.headers.get("Accept", "")
            ):
                return JsonResponse(
                    {"detail": "Authentication credentials were not provided."}, status=401
                )
            return redirect_to_login(request.get_full_path())
        return self.get_response(request)
