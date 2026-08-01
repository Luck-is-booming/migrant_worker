import hashlib

from django.conf import settings
from django.contrib import messages
<<<<<<< HEAD
=======
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.db import connection
>>>>>>> 1d670fd (refactor)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_http_methods

from blog.models import Article
from payments.tokens import make_membership_token

from payments.tokens import make_membership_token

from .forms import ContactMessageForm, MembershipForm
<<<<<<< HEAD
from .homepage import build_homepage_context
from .notifications import notify_contact_message, notify_membership_application
=======
from .homepage import build_site_context
from .models import EmergencyResource, FrequentlyAskedQuestion, OfficialResource, ResourceCategory
from .notifications import notify_contact_message, notify_membership_application


def _ip_hash(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "unknown")
    return hashlib.sha256(f"{settings.SECRET_KEY}:{ip}".encode()).hexdigest()


def _allow_contact_submission(request):
    key = f"contact-rate:{_ip_hash(request)}"
    count = cache.get(key, 0)
    if count >= 5:
        return False
    if count:
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, count + 1, 3600)
    else:
        cache.set(key, 1, 3600)
    return True


@require_GET
def index_view(request):
    return render(request, "core/home.html", build_site_context())


@require_GET
def about(request):
    return render(request, "core/about.html", build_site_context())


@require_GET
def guidance(request):
    return render(request, "core/guidance.html", build_site_context())


@require_GET
def safety(request):
    context = build_site_context()
    context["alerts"] = Article.objects.published().filter(article_type="alert")[:6]
    return render(request, "core/safety.html", context)


@require_GET
def resources(request):
    selected = request.GET.get("category", "").strip()[:160]
    resource_queryset = OfficialResource.objects.filter(is_active=True).select_related("category")
    if selected:
        resource_queryset = resource_queryset.filter(category__slug=selected)
    context = build_site_context()
    context.update(
        {
            "resources": resource_queryset,
            "resource_categories": ResourceCategory.objects.filter(is_active=True),
            "selected_category": selected,
            "emergency_resources": EmergencyResource.objects.filter(is_active=True),
        }
    )
    return render(request, "core/resources.html", context)


@require_GET
def faq(request):
    context = build_site_context()
    context["faqs"] = FrequentlyAskedQuestion.objects.filter(is_active=True)
    return render(request, "core/faq.html", context)
>>>>>>> 1d670fd (refactor)


@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "POST" and not _allow_contact_submission(request):
        messages.error(request, _("Too many submissions were received. Please try again later."))
        return redirect("contact")

    form = ContactMessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        contact_message = form.save()
        notify_contact_message(contact_message)
        messages.success(request, _("Your message was saved. Our team will review it."))
        return redirect("contact")

    context = build_site_context()
    context["form"] = form
    return render(request, "core/contact.html", context)

<<<<<<< HEAD
                token = make_membership_token(saved_membership.id)
                payment_path = reverse(
                    "payments:manual_payment",
                    kwargs={"token": token},
                )
                payment_url = request.build_absolute_uri(payment_path)
                notify_membership_application(saved_membership, payment_url)

                return redirect("payments:manual_payment", token=token)
=======
>>>>>>> 1d670fd (refactor)

@require_http_methods(["GET", "POST"])
def membership_apply(request):
    form = MembershipForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        membership = form.save(commit=False)
        membership.payment_status = "pending"
        membership.is_approved = False
        membership.save()
        token = make_membership_token(membership.id)
        path = reverse("payments:manual_payment", kwargs={"token": token})
        notify_membership_application(membership, request.build_absolute_uri(path))
        return redirect("payments:manual_payment", token=token)

<<<<<<< HEAD
            if contact_form.is_valid():
                contact = contact_form.save()
                notify_contact_message(contact)
                messages.success(request, _("Your message has been received."))
                return redirect("index")
=======
    context = build_site_context()
    context["form"] = form
    return render(request, "core/membership_apply.html", context)
>>>>>>> 1d670fd (refactor)


<<<<<<< HEAD
    return render(request, "core/index.html", context)
=======
@require_GET
def robots_txt(request):
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            "Disallow: /en/admin/",
            "Disallow: /ne/admin/",
            "Disallow: /i18n/",
            "Disallow: /en/payments/",
            "Disallow: /ne/payments/",
            "Disallow: /en/counseling/submitted/",
            "Disallow: /ne/counseling/submitted/",
            f"Sitemap: {settings.SITE_URL}/sitemap.xml",
            "",
        ]
    )
    return HttpResponse(body, content_type="text/plain")


@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
>>>>>>> 1d670fd (refactor)
