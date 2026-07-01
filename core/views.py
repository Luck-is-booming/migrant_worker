from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from .forms import ContactMessageForm, MembershipForm
from .homepage import build_homepage_context


def create_admin_view(request):
    username = "admin"
    password = "admin"
    email = "kheshahang44668800@gmail.com"

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        return HttpResponse(f"Admin '{username}' created successfully!")
    return HttpResponse("Admin already exists.")


@require_http_methods(["GET", "POST"])
def index_view(request):
    membership_form = MembershipForm()
    contact_form = ContactMessageForm()

    if request.method == "POST":
        if "membership_submit" in request.POST:
            membership_form = MembershipForm(request.POST)

            if membership_form.is_valid():
                saved_membership = membership_form.save(commit=False)
                saved_membership.payment_status = "pending"
                saved_membership.is_approved = False
                saved_membership.save()

                return redirect(
                    "payments:manual_payment",
                    membership_id=saved_membership.id
                )

        elif "contact_submit" in request.POST:
            contact_form = ContactMessageForm(request.POST)

            if contact_form.is_valid():
                contact_form.save()
                messages.success(request, _("Your message has been received."))
                return redirect("index")

    context = build_homepage_context()
    context["membership_form"] = membership_form
    context["contact_form"] = contact_form

    return render(request, "core/index.html", context)