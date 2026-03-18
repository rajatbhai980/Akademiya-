from rest_framework import serializers
from base.models import * 

class SemesterSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Semester
        fields = '__all__'

    def create(self, validated_data):
        name = validated_data.get('name')
        obj, created = Semester.objects.get_or_create(name=name)
        return obj

class SubjectSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Subject
        fields = '__all__'

    def create(self, validated_data):
        name = validated_data.get('name')
        obj, created = Subject.objects.get_or_create(name=name)
        return obj

class QuestionPageSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = QuestionPage
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Answer
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Question
        fields = '__all__'