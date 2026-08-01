import hashlib
import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from .forms import CounselingRequestForm
from .notifications import notify_staff_new_request


logger = logging.getLogger(__name__)


def _client_key(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    raw_ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "unknown")
    return hashlib.sha256(f"{settings.SECRET_KEY}:{raw_ip}".encode("utf-8")).hexdigest()


def _rate_limited(request):
    key = f"counseling-rate:{_client_key(request)}"
    current = cache.get(key, 0)
    if current >= settings.COUNSELING_RATE_LIMIT_PER_HOUR:
        return True
    if current == 0:
        cache.set(key, 1, timeout=3600)
    else:
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, current + 1, timeout=3600)
    return False


@require_http_methods(["GET", "POST"])
def request_counseling(request):
    if request.method == "POST" and _rate_limited(request):
        return render(request, "errors/429.html", status=429)

    form = CounselingRequestForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        submission = form.save(commit=False)
        submission.source_ip_hash = _client_key(request)
        submission.save()
        logger.info(
            "Counseling request created reference=%s category=%s",
            submission.public_id,
            submission.category_id,
        )
        notify_staff_new_request(submission)
        request.session["counseling_reference"] = str(submission.public_id)
        return redirect("counseling:success")

    return render(request, "counseling/request.html", {"form": form})


def success(request):
    reference = request.session.pop("counseling_reference", "")
    return render(request, "counseling/success.html", {"reference": reference})
