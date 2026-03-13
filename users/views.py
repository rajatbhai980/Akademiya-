from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import random
from .serializers import * 
from .models import * 
from django.core.mail import send_mail
# Create your views here.

@api_view(['POST'])
def otp_request(request): 
    otp = random.randint(100000, 999999)

    serializer = EmailSerializer(data=request.data)
    if serializer.is_valid(): 
        email = serializer.data['email']

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

    
class EmailRegister(APIView): 
    def post(self, request): 
        pass