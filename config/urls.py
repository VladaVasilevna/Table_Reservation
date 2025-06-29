from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from users.views import delete_profile

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("reserv.urls", namespace="reserv")),
    path("users/", include("users.urls", namespace="users")),
    path("api/profile/delete/", delete_profile, name="api_delete_profile"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
