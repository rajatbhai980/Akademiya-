from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import * 
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
