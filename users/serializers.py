from rest_framework import serializers


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField(min_value=100000, max_value=999999)