from django.db import models 

class OTP(models.Model): 
    email = models.CharField(max_length=50)
    otp = models.IntegerField(unique=True)