from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import * 
from base.models import * 
from django.views.decorators.cache import cache_page

@cache_page(60 * 10)
@api_view(['get'])
def show_leaderboard(request): 
    top_guys = Scholar.objects.all().order_by('-performance__level')[:10]
    serializers = ScholarPerformanceSerializer(top_guys, many=True)

    return Response(serializers.data, status=status.HTTP_200_OK)