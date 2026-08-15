import logging
import random

from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.mail import send_mail
from django.middleware.csrf import get_token
from random_username.generate import generate_username
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import OTP
from .serializers import EmailSerializer, OTPSerializer
from base.models import Scholar

import resend

resend.api_key = settings.RESEND_API_KEY

logger = logging.getLogger(__name__)


class OTPRequestThrottle(AnonRateThrottle):
    rate = '5/min'


class OTPVerificationThrottle(AnonRateThrottle):
    rate = '10/min'


def serialize_user(user):
    return {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'is_staff': user.is_staff,
    }


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_cookie(request):
    token = get_token(request)
    return Response(
        {'detail': 'CSRF cookie set.', 'csrfToken': token},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRequestThrottle])
def otp_request(request):
    serializer = EmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email'].lower()
    otp = random.randint(100000, 999999)

    OTP.objects.filter(email=email).delete()
    OTP.objects.create(email=email, otp=otp)

    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": email,
            "subject": 'Akademiya OTP',
            "html": f"<p>Your OTP is <strong>{otp}</strong></p>"
            })

    except Exception as exc:
        logger.exception('Failed to send OTP email to %s', email)

    return Response(
        {'detail': 'OTP sent successfully.', 'email': email},
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPVerificationThrottle])
def otp_verification(request):
    serializer = OTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    otp = serializer.validated_data['otp']
    email = serializer.validated_data['email'].lower()

    otp_record = OTP.objects.filter(otp=otp, email=email).order_by('-created_at').first()
    if not otp_record:
        return Response({'detail': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

    user = Scholar.objects.filter(email=email).first()
    if user is None:
        generated_username = generate_username()
        username = generated_username[0] if isinstance(generated_username, (list, tuple)) else generated_username
        user = Scholar.objects.create(email=email, username=username)

    if not user.is_active:
        return Response({'detail': 'User account is inactive.'}, status=status.HTTP_403_FORBIDDEN)

    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return Response(
        {
            'detail': 'Authentication successful.',
            'authenticated': True,
            'user': serialize_user(user),
        },
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def me(request):
    if request.user.is_authenticated:
        return Response({'authenticated': True, 'user': serialize_user(request.user)}, status=status.HTTP_200_OK)

    return Response({'authenticated': False, 'user': None}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_view(request):
    auth_logout(request)
    return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)

