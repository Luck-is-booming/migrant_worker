from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from payments.tokens import make_membership_token

from .forms import ContactMessageForm, MembershipForm
from .homepage import build_homepage_context
from .notifications import notify_contact_message, notify_membership_application


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

                token = make_membership_token(saved_membership.id)
                payment_path = reverse(
                    "payments:manual_payment",
                    kwargs={"token": token},
                )
                payment_url = request.build_absolute_uri(payment_path)
                notify_membership_application(saved_membership, payment_url)

                return redirect("payments:manual_payment", token=token)

        elif "contact_submit" in request.POST:
            contact_form = ContactMessageForm(request.POST)

            if contact_form.is_valid():
                contact = contact_form.save()
                notify_contact_message(contact)
                messages.success(request, _("Your message has been received."))
                return redirect("index")

    context = build_homepage_context()
    context["membership_form"] = membership_form
    context["contact_form"] = contact_form

    return render(request, "core/index.html", context)
