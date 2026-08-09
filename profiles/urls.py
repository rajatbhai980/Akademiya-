from django.urls import path, include
from .views import * 

urlpatterns = [
    path('search/', search_profiles, name='search_profiles'),
    path('update/', UpdateProfile.as_view(), name='update_profile'),
    path('<int:pk>/', ViewProfile.as_view(), name='view_profile'),
]