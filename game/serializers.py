from rest_framework import serializers
from base.models import *

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'name']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name'] 

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'description', 'correct']

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'description', 'hint', 'full_explaination', 'answers']

class QuestionPageSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = QuestionPage
        fields = ['id', 'subject', 'year']

class QuestionPageDetailSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = QuestionPage
        fields = ['id', 'subject', 'year', 'questions']


class PerformanceSerializer(serializers.Serializer): 
    experience = serializers.IntegerField()
    attempted = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    level = serializers.IntegerField()
