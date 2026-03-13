from rest_framework import serializers

class EmailSerializer(serializers.Serializer): 
    email = serializers.CharField()

class OTPSerializer(serializers.Serializer): 
    email = serializers.CharField()
    otp = serializers.IntegerField()