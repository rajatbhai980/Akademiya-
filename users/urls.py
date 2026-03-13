from django.urls import path 
from .views import * 
urlpatterns = [
    path('otp_request/', otp_request, name='otp_request'), 
    path('email_register/', EmailRegister.as_view(), name='email_register')
]
