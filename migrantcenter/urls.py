from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core import views as core_views
from core.sitemaps import ArticleSitemap, MemberSitemap, StaticViewSitemap


sitemaps = {
    "static": StaticViewSitemap,
    "articles": ArticleSitemap,
    "members": MemberSitemap,
}


# URLs without language prefixes
urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("robots.txt", core_views.robots_txt, name="robots_txt"),
    path("health/", core_views.health, name="health"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]


# Public URLs with /ne/ and /en/ prefixes
urlpatterns += i18n_patterns(
    path("", include("core.urls")),
    path("members/", include("members.urls")),
    path("news/", include("blog.urls")),
)


handler404 = "migrantcenter.error_views.page_not_found"
handler500 = "migrantcenter.error_views.server_error"