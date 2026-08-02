from django.urls import path

from . import views

app_name = "counseling"

urlpatterns = [
    path("", views.request_counseling, name="request"),
    path("submitted/", views.success, name="success"),
]
