from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from base.models import Semester, Subject, QuestionPage, GameSession, QuizPlan, Answer, Question, Scholar, Performance

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
        url = reverse('view_semesters_user')
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
        url = reverse('view_subjects_user', kwargs={'semester_id': self.semester1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        subject_names = [subject['name'] for subject in response.data]
        self.assertIn('Mathematics', subject_names)
        self.assertIn('Physics', subject_names)

    def test_view_page_count(self):
        """Test POST /game/page_count/ returns page counts for subjects"""
        url = reverse('view_pages_counts_user')
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

    def test_view_question_pages(self):
        session = GameSession.objects.create(mode='select')
        plan = QuizPlan.objects.create(game_session=session)

        page1 = self.subject1.pages.first()
        page2 = self.subject3.pages.first()
        plan.pages.add(page1, page2)

        url = reverse('view_question_pages', kwargs={'game_session_id': session.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        returned_ids = {item['id'] for item in response.data}
        self.assertSetEqual(returned_ids, {page1.id, page2.id})

        for item in response.data:
            self.assertIn('subject', item)
            self.assertIn('year', item)

    def test_view_question_page_detail(self):
        page = self.subject1.pages.first()
        question = Question.objects.create(
            description='Sample question',
            subject=self.subject1,
            page=page,
            hint='Sample hint',
            full_explaination='Sample explanation'
        )
        answer1 = Answer.objects.create(question=question, description='Answer 1', correct=True)
        answer2 = Answer.objects.create(question=question, description='Answer 2', correct=False)

        url = reverse('view_question_page_detail', kwargs={'page_id': page.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], page.id)
        self.assertEqual(response.data['subject']['id'], self.subject1.id)
        self.assertEqual(response.data['year'], str(page.year))
        self.assertIn('questions', response.data)
        self.assertEqual(len(response.data['questions']), 1)

        question_data = response.data['questions'][0]
        self.assertEqual(question_data['description'], 'Sample question')
        self.assertIn('answers', question_data)
        self.assertEqual(len(question_data['answers']), 2)
        self.assertTrue(any(answer['description'] == 'Answer 1' and answer['correct'] for answer in question_data['answers']))
        self.assertTrue(any(answer['description'] == 'Answer 2' and not answer['correct'] for answer in question_data['answers']))


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


class SubmitAnswerTestCase(GameViewsTestCase):
    def test_submit_answer(self):
        # Create a game session and quiz plan
        session = GameSession.objects.create(mode='select')
        plan = QuizPlan.objects.create(game_session=session)
        plan.pages.add(self.subject1.pages.first())  # Add a page

        # Create answers for the question
        question = self.subject1.pages.first().questions.first()
        correct_answer = Answer.objects.create(question=question, description="Correct", correct=True)
        wrong_answer = Answer.objects.create(question=question, description="Wrong", correct=False)

        url = reverse('submit_answer')
        data = {
            'game_session_id': session.id,
            'answers': [
                {'answer_id': correct_answer.id},
                {'answer_id': wrong_answer.id}
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['correct_answers'], 1)
        self.assertEqual(response.data['index_no'], 1)

        session.refresh_from_db()
        self.assertEqual(session.correct_answers, 1)
        self.assertEqual(session.current_index, 1)


class PerformanceUpdateTestCase(GameViewsTestCase):
    def setUp(self):
        super().setUp()
        self.scholar = Scholar.objects.create(email='test@example.com', password='testpass')
        self.client.force_authenticate(user=self.scholar)

    def test_display_and_update_performance_normal(self):
        # Scholar and performance are created automatically via signal
        scholar = self.scholar
        performance = scholar.performance
        performance.experience = 500
        performance.save()
        
        session = GameSession.objects.create(user=scholar, mode='select', current_index=2, correct_answers=3)
        plan = QuizPlan.objects.create(game_session=session)
        plan.pages.add(self.subject1.pages.first())

        url = reverse('display_and_update_performance')
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['experience'], 790)  # 500 + (2*10*10) + (3*30) = 500 + 200 + 90 = 790
        self.assertEqual(response.data['attempted'], 20)  # 2 * 10
        self.assertEqual(response.data['correct_answers'], 3)
        self.assertEqual(response.data['level'], 1)

        performance.refresh_from_db()
        self.assertEqual(performance.experience, 790)
        self.assertEqual(performance.attempted, 20)
        self.assertEqual(performance.correct, 3)
        self.assertEqual(performance.level, 1)

        # Check that session is deleted
        with self.assertRaises(GameSession.DoesNotExist):
            session.refresh_from_db()

    def test_display_and_update_performance_with_level_up(self):
        # Scholar and performance are created automatically via signal
        scholar = self.scholar
        performance = scholar.performance
        performance.experience = 950
        performance.save()
        
        session = GameSession.objects.create(user=scholar, mode='select', current_index=1, correct_answers=2)
        plan = QuizPlan.objects.create(game_session=session)
        plan.pages.add(self.subject1.pages.first())

        url = reverse('display_and_update_performance')
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 950 + (1*10*10) + (2*30) = 950 + 100 + 60 = 1110
        # 1110 > 1000, so level +=1, experience = 1110 % 1000 = 110
        self.assertEqual(response.data['experience'], 110)
        self.assertEqual(response.data['attempted'], 10)
        self.assertEqual(response.data['correct_answers'], 2)
        self.assertEqual(response.data['level'], 2)

        performance.refresh_from_db()
        self.assertEqual(performance.experience, 110)
        self.assertEqual(performance.attempted, 10)
        self.assertEqual(performance.correct, 2)
        self.assertEqual(performance.level, 2)

    def test_display_and_update_performance_no_quiz_plan(self):
        # Scholar and performance are created automatically via signal
        scholar = self.scholar
        performance = scholar.performance
        performance.experience = 500
        performance.save()
        
        session = GameSession.objects.create(user=scholar, mode='select', current_index=1, correct_answers=1)
        # No quiz plan created

        url = reverse('display_and_update_performance')
        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'quiz plan doesnt exists!')

        # Performance should not be updated
        performance.refresh_from_db()
        self.assertEqual(performance.experience, 500)
        self.assertEqual(performance.attempted, 0)
        self.assertEqual(performance.correct, 0)

        # Session should still exist
        session.refresh_from_db()
        self.assertEqual(session.current_index, 1)




