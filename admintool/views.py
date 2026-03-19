from base.models import * 
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import * 
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class EnterPage(APIView):  
    '''
    {
  "semester": {"name": ""},
  "subject": {"name": ""},
  "question_page": {"year": ""},
  "question_answers": [
    {
    "description": "",
    "hint": "",
    "full_explaination": "",
    "answers": [
      {"description": "", "correct": },
      {"description": "", "correct": },
      {"description": "", "correct": },
      {"description": "", "correct": }
    ]
    }
  ]
}
    '''
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request): 
        subject = request.data.get('subject')
        semester = request.data.get('semester')
        question_page = request.data.get('question_page')
        questions = request.data.get('question_answers', [])
         
        subject_serializer = SubjectSerializer(data=subject)
        semester_serializer = SemesterSerializer(data=semester)
        question_page_serializer = QuestionPageSerializer(data=question_page)

        errors = {}
        if not semester_serializer.is_valid():
            errors['semester'] = semester_serializer.errors
        if not subject_serializer.is_valid():
            errors['subject'] = subject_serializer.errors
        if not question_page_serializer.is_valid():
            errors['question_page'] = question_page_serializer.errors

        if errors: 
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        

        with transaction.atomic(): 
            semester = semester_serializer.save()

            subject = subject_serializer.save()
            subject.semester = semester
            subject.save() 

            question_page = question_page_serializer.save()           

            for Question in questions: 
                question_serializer = QuestionSerializer(data=Question)
                if question_serializer.is_valid(): 
                    question = question_serializer.save()
                    question.page = question_page
                    question.subject = subject
                    question.save()
                    answers = Question.get('answers', [])
                    for answer in answers: 
                        answer_serializer = AnswerSerializer(data=answer)
                        if answer_serializer.is_valid():
                            answer = answer_serializer.save()
                            answer.question = question 
                            answer.save()
                        else: 
                            return Response({'error': answer_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else: 
                    return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_201_CREATED)
        
class ViewPage(APIView): 
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, year): 
        page = QuestionPage.objects.prefetch_related('questions__answers').get(year=year)
        question = page.questions.first()
        subject = question.subject 
        semester = subject.semester 
        Questions = page.questions.all()

        data = {
            'semester': SemesterSerializer(semester).data, 
            'subject': SubjectSerializer(subject).data, 
            'page': QuestionPageSerializer(page).data, 
        }
        for i, question in enumerate(Questions, 1): 
            data[f'question {i}'] = {'question': QuestionSerializer(question).data}
            Answers = question.answers.all()
            for j, answer in enumerate(Answers, 1): 
                data[f'question {i}'][f'answer {j}'] = AnswerSerializer(answer).data
        return Response(data, status=status.HTTP_200_OK)

class UpdatePage(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    '''
        page, semester and subjects are queried directly 
        questions and answers and querid through their ids 
    '''
    def put(self, request, year):
        try: 
            page = QuestionPage.objects.get(year=year)
        except QuestionPage.DoesNotExist: 
            return Response({'error': 'page doesnt not exists'},status=status.HTTP_400_BAD_REQUEST)

        first_question = page.questions.first()
        subject = first_question.subject
        semester = subject.semester 
        
        page_data = request.data.get('page')
        subject_data = request.data.get('subject')
        semester_data = request.data.get('semester')

        page_serializer = QuestionPageSerializer(page, data=page_data)
        subject_serializer = SubjectSerializer(subject, data=subject_data)
        semester_serializer = SemesterSerializer(semester, data=semester_data)

        with transaction.atomic():
            errors = {}

            if not page_serializer.is_valid(): 
                errors['page_error'] = page_serializer.errors
            
            if not subject_serializer.is_valid(): 
                errors['subject_error'] = subject_serializer.errors

            if not semester_serializer.is_valid(): 
                errors['semester_error'] = semester_serializer.errors

            if errors: 
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

            page_serializer.save()
            subject_serializer.save()
            semester_serializer.save()
            
            questions = request.data.get('question_answers', [])
            for question_data in questions:
                q_id = question_data.get('id') 
                question_instance = Question.objects.get(pk=q_id)
                question_serializer = QuestionSerializer(question_instance, data=question_data)
                if question_serializer.is_valid(): 
                    question_serializer.save()
                else: 
                    return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                answers = question_data.get('answers', [])
                for answer_data in answers: 
                    a_id = answer_data.get('id')
                    answer_instance = Answer.objects.get(pk=a_id)
                    answer_serializer = AnswerSerializer(answer_instance, data=answer_data)
                    if answer_serializer.is_valid(): 
                        answer_serializer.save()
                    else: 
                        return Response(answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_200_OK)

            

class DeletePage(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def delete(self, request, year):
        page = QuestionPage.objects.get(year=year)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)