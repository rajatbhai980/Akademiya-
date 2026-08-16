from django.urls import path, include
from .views import * 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('search/', search_profiles, name='search_profiles'),
    path('update/', UpdateProfile.as_view(), name='update_profile'),
    path('<int:pk>/', ViewProfile.as_view(), name='view_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)