from rest_framework import serializers
from base.models import * 

class SemesterSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Semester
        fields = ['name']

    def create(self, validated_data):
        name = validated_data.get('name')
        obj, created = Semester.objects.get_or_create(name=name)
        return obj

class SubjectSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Subject
        fields = ['name']

    def create(self, validated_data):
        name = validated_data.get('name')
        obj, created = Subject.objects.get_or_create(name=name)
        return obj

class QuestionPageSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = QuestionPage
        fields = ['year']

    def create(self, validated_data):
        year = validated_data.get('year')
        obj, created = QuestionPage.objects.get_or_create(year=year)
        return obj

class AnswerSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Answer
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Question
        fields = '__all__'

class QuestionsAnswerSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Answer
        fields = ['description', 'correct']

