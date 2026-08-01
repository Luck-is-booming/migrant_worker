from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
<<<<<<< HEAD
=======
    path("about/", views.about, name="about"),
    path("guidance/", views.guidance, name="guidance"),
    path("safety/", views.safety, name="safety"),
    path("resources/", views.resources, name="resources"),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),
    path("membership/apply/", views.membership_apply, name="membership_apply"),
    path("counseling/", include("counseling.urls")),
>>>>>>> 1d670fd (refactor)
    path("payments/", include("payments.urls")),
]
