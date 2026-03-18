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
  "question_answer": {
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
}
    '''
    permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request): 
        subject = request.data.get('subject')
        semester = request.data.get('semester')
        question_page = request.data.get('question_page')
        question = request.data.get('question_answer', {})
        answers = request.data.get('question_answer', {}).get('answers')
         
        subject_serializer = SubjectSerializer(data=subject)
        semester_serializer = SemesterSerializer(data=semester)
        question_page_serializer = QuestionPageSerializer(data=question_page)
        question_serializer = QuestionSerializer(data=question)

        errors = {}
        if not semester_serializer.is_valid():
            errors['semester'] = semester_serializer.errors
        if not subject_serializer.is_valid():
            errors['subject'] = subject_serializer.errors
        if not question_page_serializer.is_valid():
            errors['question_page'] = question_page_serializer.errors
        if not question_serializer.is_valid():
            errors['question'] = question_serializer.errors

        if errors: 
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        

        with transaction.atomic(): 
            semester = semester_serializer.save()

            subject = subject_serializer.save()
            subject.semester = semester
            subject.save() 

            question_page = question_page_serializer.save()
   
            question = question_serializer.save()
            question.page = question_page
            question.subject = subject
            question.save()

            for answer in answers: 
                answer_serializer = AnswerSerializer(data=answer)
                if answer_serializer.is_valid():
                    answer = answer_serializer.save()
                    answer.question = question 
                    answer.save()
                else: 
                    return Response({'error': answer_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
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
                data[f'question {i}'][f'answer {j}'] = QuestionsAnswerSerializer(answer).data
        return Response(data, status=status.HTTP_200_OK)

class DeletePage(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser] 
    def delete(self, request, year): 
        page = QuestionPage.objects.get(year=year)  
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)