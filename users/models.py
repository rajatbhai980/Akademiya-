from django.db import models 

class OTP(models.Model): 
    email = models.CharField(max_length=50, unique=True)
    otp = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)