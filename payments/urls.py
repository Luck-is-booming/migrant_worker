from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("pay/<str:token>/", views.manual_payment_view, name="manual_payment"),
    path("status/<str:token>/", views.payment_pending_view, name="payment_pending"),
]
