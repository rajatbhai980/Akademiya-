from django.urls import path, include
from .views import * 
urlpatterns = [
    path('otp_request/', otp_request, name='otp_request'), 
    path('otp_verification/', otp_verification, name='otp_verification'), 
    path('accounts/', include('allauth.urls')),
]
