from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

# Keep the i18n switcher view OUTSIDE the i18n_patterns wrapper
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Required for processing language form submissions
]

# Wrap your admin and app URLs INSIDE i18n_patterns
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('core.urls')), 
    path("members/", include("members.urls")),                                  # Includes app-level routing with language prefixes
)