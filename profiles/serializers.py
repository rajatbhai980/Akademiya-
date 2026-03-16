from base.models import *  
from rest_framework import serializers

class ViewProfileSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Scholar
        exclude = ['email', 'password', 'is_staff', 'is_active', 'groups', 'user_permissions']

class ViewPerformanceSerializer(serializers.ModelSerializer): 
    correct_ratio = models.DecimalField()
    class Meta: 
        model = Performance 
        fields = ['id', 'level', 'experience', 'attempted', 'correct', 'correct_ratio']

class ScholarSerializer(serializers.Serializer):
    id = serializers.IntegerField() 
    username = serializers.CharField()

class FullProfileSerializer(serializers.Serializer): 
    profile_info = ViewProfileSerializer()
    performance_info = ViewPerformanceSerializer()
    follower_count = serializers.IntegerField()
    followee_count = serializers.IntegerField()
    followers = serializers.ListField(child=ScholarSerializer())
    followees = serializers.ListField(child=ScholarSerializer())
