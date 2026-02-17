from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sentry-debug/', trigger_error),
    path('amigos/', include('beats.amizades.urls', namespace='amizades')),
    path('profile/', include('beats.profiles.urls', namespace='profiles')),
    path('', include('beats.playlist.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)