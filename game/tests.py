from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from base.models import Semester, Subject, QuestionPage, GameSession, QuizPlan

class GameViewsTestCase(APITestCase):
    def setUp(self):
        self.semester1 = Semester.objects.create(name="Semester 1")
        self.semester2 = Semester.objects.create(name="Semester 2")

        self.subject1 = Subject.objects.create(name="Mathematics", semester=self.semester1)
        self.subject2 = Subject.objects.create(name="Physics", semester=self.semester1)
        self.subject3 = Subject.objects.create(name="Chemistry", semester=self.semester2)

        QuestionPage.objects.create(subject=self.subject1, year="2023-01-01")
        QuestionPage.objects.create(subject=self.subject1, year="2023-01-02")
        QuestionPage.objects.create(subject=self.subject2, year="2023-01-01")
        QuestionPage.objects.create(subject=self.subject3, year="2023-01-01")
        QuestionPage.objects.create(subject=self.subject3, year="2023-01-02")
        QuestionPage.objects.create(subject=self.subject3, year="2023-01-03")

    def test_view_semesters(self):
        url = reverse('view_semesters')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        semester_names = [semester['name'] for semester in response.data]
        self.assertIn('Semester 1', semester_names)
        self.assertIn('Semester 2', semester_names)

        semester_ids = [semester['id'] for semester in response.data]
        self.assertIn(self.semester1.id, semester_ids)
        self.assertIn(self.semester2.id, semester_ids)

    def test_view_subjects_valid_semester(self):
        url = reverse('view_subjects', kwargs={'semester_id': self.semester1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        subject_names = [subject['name'] for subject in response.data]
        self.assertIn('Mathematics', subject_names)
        self.assertIn('Physics', subject_names)

    def test_view_page_count(self):
        """Test POST /game/page_count/ returns page counts for subjects"""
        url = reverse('view_pages_counts')
        data = {
            'subjects': [
                {'subject_name': 'Mathematics', 'id': self.subject1.id},
                {'subject_name': 'Chemistry', 'id': self.subject3.id}
            ]
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('Mathematics', response.data)
        self.assertIn('Chemistry', response.data)

        self.assertEqual(response.data['Mathematics'], 2)
        self.assertEqual(response.data['Chemistry'], 3)


class StartGameTestCase(GameViewsTestCase):
    def test_start_game_select(self):
        url = reverse('start_game')
        data = {
            'mode': 'select',
            'subject': {'id': self.subject1.id, 'pages': 1},
            'order': 'asc'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        plan = QuizPlan.objects.get(id=response.data['quiz_plan_id'])
        self.assertEqual(plan.pages.count(), 1)
        self.assertEqual(plan.pages.first().subject, self.subject1)

    def test_start_game_custom(self):
        url = reverse('start_game')
        data = {
            'mode': 'custom',
            'subjects': [
                {'id': self.subject1.id, 'pages': 1},
                {'id': self.subject3.id, 'pages': 2}
            ],
            'order': 'asc'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        plan = QuizPlan.objects.get(id=response.data['quiz_plan_id'])
        self.assertEqual(plan.pages.count(), 3)

        subject_ids = set(plan.pages.values_list('subject_id', flat=True))
        self.assertEqual(subject_ids, {self.subject1.id, self.subject3.id})

    def test_start_game_all_mode_only_complete_subject_multiples(self):
        url = reverse('start_game')
        data = {
            'mode': 'all',
            'pages': 4,
            'order': 'asc'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        plan = QuizPlan.objects.get(id=response.data['quiz_plan_id'])
        self.assertEqual(plan.pages.count(), 3)

    def test_min_subjects_required_in_all(self):
        url = reverse('start_game')
        data = {
            'mode': 'all',
            'pages': 2,
            'order': 'asc'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Total pages must be at least number of subjects for all mode')


