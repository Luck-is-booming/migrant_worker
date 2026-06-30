from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<int:membership_id>/', views.initiate_payment, name='initiate_payment'),
    path('success/', views.esewa_success, name='payment_success'),
    path('failure/', views.esewa_failure, name='payment_failure'),
]