from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import random
from .serializers import * 
from .models import * 
from base.models import * 
from django.core.mail import send_mail
from random_username.generate import generate_username
# Create your views here.

@api_view(['POST'])
def otp_request(request): 
    otp = random.randint(100000, 999999)

    serializer = EmailSerializer(data=request.data)
    if serializer.is_valid(): 
        email = serializer.data['email']
        
        previous = OTP.objects.filter(email=email).exists()
        if previous: 
            OTP.objects.filter(email=email).delete()

        OTP.objects.create( 
            email = email,  
            otp = otp 
        )

        send_mail(
        "Akademiya OTP",
        otp,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,)

        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def otp_verification(request): 
    serializer = OTPSerializer(data=request.data)
    if serializer.is_valid(): 
        otp = serializer.validated_data['otp']
        email = serializer.validated_data['email']

        verification = OTP.objects.filter(otp=otp, email=email).exists()

        if verification: 
            try: 
                user = Scholar.objects.get(email=email)
            except: 
                user = None
            if user is not None: 
                login(request, user)
            else: 
                new_username = generate_username()
                new_user = Scholar.objects.create(email=email, username=new_username[0])
                login(request, new_user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_400_BAD_REQUEST)

##to test this thing out 
    
