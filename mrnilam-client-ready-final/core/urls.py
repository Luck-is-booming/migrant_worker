from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("about/", views.about, name="about"),
    path("guidance/", views.guidance, name="guidance"),
    path("safety/", views.safety, name="safety"),
    path("resources/", views.resources, name="resources"),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),
    path("membership/", views.membership_information, name="membership_information"),
    path("membership/apply/", views.membership_apply, name="membership_apply"),
    path("programs/", views.programs, name="programs"),
    path("privacy/", views.privacy, name="privacy"),
    path("disclaimer/", views.disclaimer, name="disclaimer"),
    path("counseling/", include("counseling.urls")),
    path("payments/", include("payments.urls")),
]
