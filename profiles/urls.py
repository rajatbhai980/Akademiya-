from django.urls import path, include
from .views import * 
urlpatterns = [
    path('<int:pk>/', ViewProfile.as_view(), name='view_profile')
]