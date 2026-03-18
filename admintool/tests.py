from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from base.models import Semester, Subject, QuestionPage, Question, Answer, Scholar

class EnterPageViewTest(APITestCase):
    def setUp(self): 
        self.url = reverse('enter_page') 
        self.user = Scholar.objects.create_superuser(email='super@gmail.com')
        self.client.force_login(self.user)
        self.valid_payload = {
  "semester": {"name": "Fall"},
  "subject": {"name": "Mathematics"},
  "question_page": {"year": "2024-03-17"},
  "question_answer": {
    "description": "What is 2 + 2?",
    "hint": "Think about simple addition",
    "full_explaination": "Adding 2 and 2 gives 4 because it is basic arithmetic.",
    "answers": [
      {"description": "1", "correct": False},
      {"description": "2", "correct": False},
      {"description": "3", "correct": False},
      {"description": "4", "correct": True}
    ]
  }
}

    def test_creates_all_objects(self):
        response = self.client.post(self.url, format='json', data=self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Semester.objects.count(), 1)
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(QuestionPage.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Answer.objects.count(), 4)

    def test_question_to_subject_and_page(self):
        self.client.post(self.url, format='json', data=self.valid_payload)

        subject = Subject.objects.first()
        page = QuestionPage.objects.first()
        self.assertIsNotNone(subject.questions)
        self.assertIsNotNone(page.questions)

    def test_subject_semester(self):
        self.client.post(self.url, format='json', data=self.valid_payload)

        subject = Subject.objects.first()
        self.assertIsNotNone(subject.semester)

    def test_answers_question(self):
        self.client.post(self.url, format='json', data=self.valid_payload)

        question = Question.objects.first()
        self.assertEqual(question.answers.count(), 4)

    def test_atomicity(self):
        """If one answer fails, no semester/subject/question should persist."""
        payload = {
  "semester": {"name": 123},
  "subject": {"name": "Mathematics"},
}
        self.client.post(self.url, format='json', data=payload)

        self.assertEqual(Semester.objects.count(), 0)
        self.assertEqual(Subject.objects.count(), 0)
        self.assertEqual(Question.objects.count(), 0)

    def test_authentication(self):
        user = Scholar.objects.create(email='nonsuper@gmail.com')
        self.client.force_login(user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)