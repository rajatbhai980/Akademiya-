from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import * 
from base.models import * 

class StartGame(APIView): 
    '''
        Three modes: Select, Custom, All
    '''
    def post(self, request): 
        mode = request.data.get('mode')
        pages = request.data.get('pages')

        session = GameSession.objects.create(user=request.user if request.user else None, mode=mode)
        quiz_plan = QuizPlan.objects.create(game_session=session)
        