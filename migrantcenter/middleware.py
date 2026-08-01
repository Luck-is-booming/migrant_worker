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
