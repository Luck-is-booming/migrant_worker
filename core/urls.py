from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("payments/", include("payments.urls")),
]
