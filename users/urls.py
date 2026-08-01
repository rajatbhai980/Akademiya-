from django.urls import include, path

from .views import csrf_cookie, logout_view, me, otp_request, otp_verification

urlpatterns = [
    path('csrf/', csrf_cookie, name='csrf_cookie'),
    path('otp_request/', otp_request, name='otp_request'),
    path('otp_verification/', otp_verification, name='otp_verification'),
    path('me/', me, name='me'),
    path('logout/', logout_view, name='logout'),
    path('accounts/', include('allauth.urls')),
]
