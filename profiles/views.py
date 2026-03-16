from django.shortcuts import render
from base.models import * 
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import * 
from django.db.models import Q

class ViewProfile(APIView): 
    def get(self, request, pk):
        scholar = Scholar.objects.get(pk=pk)
        performance = scholar.performance
        following_count = Follow.objects.filter(follower=scholar).count()
        follower_count =  Follow.objects.filter(followee=scholar).count()
        follow_set = Follow.objects.select_related('follower', 'followee').filter(Q(follower=scholar) | Q(followee=scholar))
        followers = []
        followees = []
        for follow_obj in follow_set: 
            if follow_obj.follower == scholar: 
                followees.append({'id': follow_obj.followee.id,'username' : follow_obj.followee.username})
            else: 
                followers.append({'id': follow_obj.follower.id,'username' : follow_obj.follower.username})
        data = {
            "profile_info": scholar, 
            "performance_info": performance, 
            "follower_count": follower_count, 
            "followee_count": following_count, 
            "followers": followers, 
            "followees": followees
        }
        serializer =FullProfileSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
