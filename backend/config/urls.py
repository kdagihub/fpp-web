from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("sysdt/", admin.site.urls),
    path("api/", include("apps.api.urls")),
]

# Media files — servis par Django en tous environnements
# (pas de nginx devant Daphne, static() ne fonctionne qu'en DEBUG=True)
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
