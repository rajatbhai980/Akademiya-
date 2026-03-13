from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import * 
from base.models import * 
import random_username
# Create your tests here.

class TestOTP(APITestCase): 
    def test_otp_creation_200(self): 
        email = "raiz41455@gmail.com"
        data = {"email": email
        }
        url = reverse('otp_request')
        response = self.client.post(url, format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        created = OTP.objects.filter(email=email).exists()
        self.assertTrue(created)
    
    def test_otp_replacement_200(self): 
        email = "raiz41455@gmail.com"
        OTP.objects.create(email=email, otp=12332)
        data = {"email": email
        }
        url = reverse('otp_request')
        response = self.client.post(url, format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        created = OTP.objects.filter(email=email).exists()
        self.assertTrue(created)
        
    def test_full_user_registration(self): 
        email = "raiz41455@gmail.com"
        OTP.objects.create(email=email, otp=111111)
        data = {"email": email, 'otp':111111
        }
        url = reverse('otp_verification')
        response = self.client.post(url, format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        created = Scholar.objects.filter(email=email).exists()
        self.assertTrue(created)

        #checking login 
        response = self.client.post(url, format='json', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)