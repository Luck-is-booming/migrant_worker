from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import StaticViewSitemap


sitemaps = {
    "static": StaticViewSitemap,
}


# URLs that should NOT receive /en/ or /ne/ prefixes
urlpatterns = [
    path(
        "i18n/",
        include("django.conf.urls.i18n"),
    ),

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]


# URLs that receive /en/ or /ne/ prefixes
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("members/", include("members.urls")),
)