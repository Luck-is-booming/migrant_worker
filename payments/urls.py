from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("<int:membership_id>/", views.manual_payment_view, name="manual_payment"),
    path("pending/<int:payment_id>/", views.payment_pending_view, name="payment_pending"),
]