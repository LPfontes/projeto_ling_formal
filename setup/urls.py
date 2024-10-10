
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.urls import path
from tfm.views import automato_view
urlpatterns = [
    path("admin/", admin.site.urls),
    path("",automato_view)
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)