from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from base.models import Semester, Subject, QuestionPage, Question, Answer, Scholar
from datetime import date 

class EnterPageViewTest(APITestCase):
    def setUp(self): 
        self.url = reverse('enter_page') 
        self.user = Scholar.objects.create_superuser(email='super@gmail.com')
        self.client.force_login(self.user)
        self.valid_payload = {
  "semester": {"name": "Fall"},
  "subject": {"name": "Mathematics"},
  "question_page": {"year": "2024-03-17"},
  "question_answers": [
      {
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
  ]
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

class DeletePageTest(APITestCase):
    def setUp(self):
        self.url = reverse('delete_page', kwargs={'year': '2024-01-01'})
        self.admin = Scholar.objects.create_superuser(email='admin@gmail.com')
        self.user = Scholar.objects.create(email='test@gmail.com')
        QuestionPage.objects.create(year='2024-01-01')

    def test_unauthenticated_gets_401(self):
        response = self.client.delete(self.url, {'year': '2024-01-01'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_normal_user_gets_403(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url, {'year': '2024-01-01'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_existing_page(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url, {'year': '2024-01-01'})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(QuestionPage.objects.filter(year='2024-01-01').exists())


class ViewPageAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = Scholar.objects.create_superuser(email='admin@gmail.com')
        self.client.force_authenticate(user=self.admin_user)

        self.semester = Semester.objects.create(name="Semester 5")
        self.subject = Subject.objects.create(name="Software Engineering", semester=self.semester)

        # Create QuestionPage
        self.page = QuestionPage.objects.create(year=date.today())

        # Create Question
        self.question1 = Question.objects.create(
            description="What is SDLC?",
            subject=self.subject,
            page=self.page,
            hint="Think software process",
            full_explaination="Structured process to develop software"
        )

        self.question2 = Question.objects.create(
            description="What is Agile?",
            subject=self.subject,
            page=self.page,
            hint="Iterative methodology",
            full_explaination="Agile is iterative software development"
        )

        # Create Answers
        self.answer1_q1 = Answer.objects.create(question=self.question1, description="Structured process", correct=True)
        self.answer2_q1 = Answer.objects.create(question=self.question1, description="Random coding", correct=False)

        self.answer1_q2 = Answer.objects.create(question=self.question2, description="Iterative", correct=True)
        self.answer2_q2 = Answer.objects.create(question=self.question2, description="Big bang", correct=False)

    def test_viewpage_get_returns_200(self):
        url = reverse('view_page', kwargs={'year': date.today().strftime('%Y-%m-%d')})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        # Check semester and subject
        self.assertIn('semester', data)
        self.assertEqual(data['semester']['name'], "Semester 5")
        self.assertIn('subject', data)
        self.assertEqual(data['subject']['name'], "Software Engineering")
        self.assertIn('page', data)

        # Check questions and answers
        self.assertIn('question 1', data)
        self.assertIn('question 2', data)

        # Check question 1
        q1_data = data['question 1']['question']
        self.assertEqual(q1_data['description'], "What is SDLC?")
        self.assertIn('answer 1', data['question 1'])
        self.assertEqual(data['question 1']['answer 1']['description'], "Structured process")
        self.assertTrue(data['question 1']['answer 1']['correct'])
        self.assertEqual(data['question 1']['answer 2']['description'], "Random coding")
        self.assertFalse(data['question 1']['answer 2']['correct'])

        # Check question 2
        q2_data = data['question 2']['question']
        self.assertEqual(q2_data['description'], "What is Agile?")
        self.assertIn('answer 1', data['question 2'])
        self.assertEqual(data['question 2']['answer 1']['description'], "Iterative")
        self.assertTrue(data['question 2']['answer 1']['correct'])


class UpdatePageAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = Scholar.objects.create_superuser(email='admin@gmail.com')
        self.client.force_authenticate(user=self.admin_user)

        self.semester = Semester.objects.create(name="Semester 5")
        self.subject = Subject.objects.create(name="Software Engineering", semester=self.semester)
        self.page = QuestionPage.objects.create(year=date(2024, 3, 17))

        self.question1 = Question.objects.create(
            description="What is SDLC?",
            subject=self.subject,
            page=self.page,
            hint="Think software process",
            full_explaination="Structured process to develop software"
        )
        self.question2 = Question.objects.create(
            description="What is Agile?",
            subject=self.subject,
            page=self.page,
            hint="Iterative methodology",
            full_explaination="Agile is iterative software development"
        )

        self.answer1_q1 = Answer.objects.create(question=self.question1, description="Structured process", correct=True)
        self.answer2_q1 = Answer.objects.create(question=self.question1, description="Random coding", correct=False)
        self.answer1_q2 = Answer.objects.create(question=self.question2, description="Iterative", correct=True)
        self.answer2_q2 = Answer.objects.create(question=self.question2, description="Big bang", correct=False)

        self.url = reverse('update_page', kwargs={'year': '2024-03-17'})
        self.valid_payload = {
            "page": {"year": "2024-03-18"},
            "subject": {"name": "Advanced Software Engineering"},
            "semester": {"name": "Semester 6"},
            "question_answers": [
                {
                    "id": self.question1.id,
                    "description": "What is SDLC updated?",
                    "hint": "Updated hint",
                    "full_explaination": "Updated explanation",
                    "answers": [
                        {"id": self.answer1_q1.id, "description": "Updated correct", "correct": True},
                        {"id": self.answer2_q1.id, "description": "Updated wrong", "correct": False}
                    ]
                },
                {
                    "id": self.question2.id,
                    "description": "What is Agile updated?",
                    "hint": "Updated agile hint",
                    "full_explaination": "Updated agile explanation",
                    "answers": [
                        {"id": self.answer1_q2.id, "description": "Updated iterative", "correct": True},
                        {"id": self.answer2_q2.id, "description": "Updated big bang", "correct": False}
                    ]
                }
            ]
        }

    def test_update_page_successful(self):
        response = self.client.put(self.url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check page updated
        self.page.refresh_from_db()
        self.assertEqual(str(self.page.year), "2024-03-18")

        # Check subject updated
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.name, "Advanced Software Engineering")

        # Check semester updated
        self.semester.refresh_from_db()
        self.assertEqual(self.semester.name, "Semester 6")

        # Check questions updated
        self.question1.refresh_from_db()
        self.assertEqual(self.question1.description, "What is SDLC updated?")
        self.assertEqual(self.question1.hint, "Updated hint")

        self.question2.refresh_from_db()
        self.assertEqual(self.question2.description, "What is Agile updated?")

        # Check answers updated
        self.answer1_q1.refresh_from_db()
        self.assertEqual(self.answer1_q1.description, "Updated correct")

    def test_update_nonexistent_page(self):
        url = reverse('update_page', kwargs={'year': '2025-01-01'})
        response = self.client.put(url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_with_invalid_data(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload['semester'] = {"name": ""}  # Invalid empty name
        response = self.client.put(self.url, data=invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('semester_error', response.data)

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.put(self.url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_access(self):
        regular_user = Scholar.objects.create(email='user@gmail.com')
        self.client.force_authenticate(user=regular_user)
        response = self.client.put(self.url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
