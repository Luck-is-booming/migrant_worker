from django.urls import path
from . import views
urlpatterns = [
    path('', views.index_view, name='index'),
    path('setup-admin-user/', views.create_admin_view, name='setup_admin_user'),
   
]