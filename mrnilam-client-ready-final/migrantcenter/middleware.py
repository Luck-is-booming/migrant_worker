class SecurityHeadersMiddleware:
    """Apply a strict public CSP while keeping Django admin functional.

    Django admin uses a small amount of trusted inline JavaScript and CSS. The
    public site remains fully nonce-free and does not allow inline execution.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def _is_admin_path(path):
        parts = [part for part in path.split("/") if part]
        return "admin" in parts

    def __call__(self, request):
        response = self.get_response(request)
        if self._is_admin_path(request.path):
            style_src = "style-src 'self' 'unsafe-inline'"
            script_src = "script-src 'self' 'unsafe-inline'"
        else:
            style_src = "style-src 'self'"
            script_src = "script-src 'self'"

        response.setdefault(
            "Content-Security-Policy",
            "; ".join(
                [
                    "default-src 'self'",
                    "img-src 'self' data: https:",
                    style_src,
                    script_src,
                    "font-src 'self' data:",
                    "connect-src 'self'",
                    "frame-ancestors 'none'",
                    "base-uri 'self'",
                    "form-action 'self'",
                    "object-src 'none'",
                ]
            ),
        )
        response.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        return response


class AdminLoginRateLimitMiddleware:
    """Limit failed administrator login attempts by hashed network address."""

    window_seconds = 15 * 60
    max_attempts = 10

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_login_post = (
            request.method == "POST"
            and request.path.rstrip("/").endswith("/admin/login")
        )
        if not is_login_post:
            return self.get_response(request)

        import hashlib

        from django.conf import settings
        from django.core.cache import cache
        from django.shortcuts import render

        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        raw_ip = (
            forwarded.split(",")[0].strip()
            if forwarded
            else request.META.get("REMOTE_ADDR", "unknown")
        )
        digest = hashlib.sha256(
            f"{settings.SECRET_KEY}:admin-login:{raw_ip}".encode("utf-8")
        ).hexdigest()
        key = f"admin-login-rate:{digest}"
        attempts = cache.get(key, 0)
        if attempts >= self.max_attempts:
            return render(request, "errors/429.html", status=429)

        response = self.get_response(request)
        if 300 <= response.status_code < 400:
            # Successful admin authentication redirects away from the login form.
            cache.delete(key)
        else:
            cache.set(key, attempts + 1, self.window_seconds)
        return response

