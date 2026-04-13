from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import * 
from base.models import * 

class StartGame(APIView): 
    '''
        Three modes: Select, Custom, All
        
        Select mode: Single subject with page count
        {
            "mode": "select",
            "subject": {"id": 1, "pages": 5},
            "order": "desc"  // "asc" or "desc" by year
        }
        
        Custom mode: Multiple subjects with individual page counts
        {
            "mode": "custom",
            "subjects": [
                {"id": 1, "pages": 3},
                {"id": 2, "pages": 4}
            ],
            "order": "desc"
        }
        
        All mode: Distribute total pages evenly across all subjects
        {
            "mode": "all",
            "pages": 10,  // total pages to distribute
            "order": "desc"
        }
        
        This selects existing QuestionPage objects and assigns them to the quiz plan.
        Assumes the frontend has verified availability.
    '''
    def post(self, request): 
        mode = request.data.get('mode')
        order = request.data.get('order', 'desc')  # default to desc
        subjects_data = request.data.get('subjects', [])
        subject_data = request.data.get('subject', {})
        total_pages = request.data.get('pages')

        if not mode:
            return Response({'error': 'Mode is required'}, status=status.HTTP_400_BAD_REQUEST)

        if order not in ['asc', 'desc']:
            return Response({'error': 'Order must be "asc" or "desc"'}, status=status.HTTP_400_BAD_REQUEST)

        session = GameSession.objects.create(user=request.user if request.user.is_authenticated else None, mode=mode)
        quiz_plan = QuizPlan.objects.create(game_session=session)

        order_by = '-year' if order == 'desc' else 'year'

        if mode == 'select':
            if not subject_data:
                return Response({'error': 'Subject data required for select mode'}, status=status.HTTP_400_BAD_REQUEST)
            
            subject_id = subject_data.get('id')
            pages = subject_data.get('pages', 0)
            
            try:
                subject = Subject.objects.get(id=subject_id)
            except Subject.DoesNotExist:
                return Response({'error': f'Subject with id {subject_id} not found'}, status=status.HTTP_404_NOT_FOUND)
            
            available_pages = QuestionPage.objects.filter(
                subject=subject, 
            ).order_by(order_by)[:pages]
            
            quiz_plan.pages.add(*available_pages)

        elif mode.lower() == 'custom':
            if not subjects_data:
                return Response({'error': 'Subjects data required for custom mode'}, status=status.HTTP_400_BAD_REQUEST)
            
            for subject_data in subjects_data:
                subject_id = subject_data.get('id')
                pages = subject_data.get('pages', 0)
                
                try:
                    subject = Subject.objects.get(id=subject_id)
                except Subject.DoesNotExist:
                    return Response({'error': f'Subject with id {subject_id} not found'}, status=status.HTTP_404_NOT_FOUND)
                
                available_pages = QuestionPage.objects.filter(
                    subject=subject, 
                ).order_by(order_by)[:pages]
                
                quiz_plan.pages.add(*available_pages)

        elif mode.lower() == 'all':
            if total_pages is None:
                return Response({'error': 'Total pages required for all mode'}, status=status.HTTP_400_BAD_REQUEST)
            
            all_subjects = Subject.objects.all()
            num_subjects = all_subjects.count()
            
            if num_subjects == 0:
                return Response({'error': 'No subjects available'}, status=status.HTTP_400_BAD_REQUEST)
            
            pages_per_subject = total_pages // num_subjects
            
            if pages_per_subject <= 0:
                return Response({'error': 'Total pages must be at least number of subjects for all mode'}, status=status.HTTP_400_BAD_REQUEST)
            
            for subject in all_subjects:
                # Get available pages ordered by year
                available_pages = QuestionPage.objects.filter(
                    subject=subject,
                ).order_by(order_by)[:pages_per_subject]
                
                quiz_plan.pages.add(*available_pages)

        return Response({
            'session_id': session.id,
            'quiz_plan_id': quiz_plan.id,
            'message': 'Game started successfully'
        })


@api_view(['get'])
def view_semesters(request): 
    semesters = Semester.objects.all()
    serializer = SemesterSerializer(semesters, many=True)
    return Response(serializer.data)

@api_view(['get'])
def view_subjects(request, semester_id):
    try:
        semester = Semester.objects.get(id=semester_id)
        subjects = Subject.objects.filter(semester=semester)
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    except Semester.DoesNotExist:
        return Response({'error': 'Semester not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['post'])
def view_pages_counts(request):         
    """
    Get the count of question pages for multiple subjects.

    Frontend should send a POST request with the following payload format:
    {
        "subjects": [
            {
                "subject_name": "Mathematics",
                "id": 1
            },
            {
                "subject_name": "Physics", 
                "id": 2
            }
        ]
    }
    """
    subjects = request.data.get('subjects', [])
    data = {}
    for subject in subjects: 
        subject_name = subject.get('subject_name')
        subject_id = subject.get('id')
        subject = Subject.objects.get(id=subject_id)
        page_count = QuestionPage.objects.filter(subject=subject).count()
        data[subject_name] = page_count
    return Response(data)

@api_view(['post'])
def submit_answer(request):
    """
    Submit answers for the current game session page and update game progress.

    This function processes user-submitted answers for a specific game session,
    calculates the number of correct answers, updates the user's performance,
    and advances to the next page in the quiz.

    **Request Format:**
    POST /game/submit_answer/
    {
        "game_session_id": 1,
        "answers": [
            {"answer_id": 1},
            {"answer_id": 2},
            ...
        ]
    }

    **Parameters:**
    - game_session_id (int): The ID of the current game session.
    - answers (list): List of dictionaries containing answer_id for each submitted answer.
    """
    answers_data = request.data.get('answers')
    game_session_id = request.data.get('game_session_id')
    game_session = GameSession.objects.get(id=game_session_id)

    correct_count = 0
    for answer_data in answers_data:
        answer_id = answer_data.get('answer_id')
        answer = Answer.objects.get(id=answer_id)
        if answer.correct:
            correct_count += 1

    game_session.correct_answers += correct_count
    game_session.current_index += 1
    game_session.save()

    return Response({'correct_answers': correct_count, 'index_no': game_session.current_index}, status=status.HTTP_200_OK)

@api_view(['get'])
def view_question_pages(request, game_session_id): 
    game_session = GameSession.objects.get(id=game_session_id)
    quiz_plan = game_session.quiz_plan 
    question_pages = quiz_plan.pages.all()
    qp_serializers = QuestionPageSerializer(question_pages, many=True)

    return Response(qp_serializers.data, status=status.HTTP_200_OK)

@api_view(['get'])
def view_question_page_detail(request, page_id):
    try:
        question_page = QuestionPage.objects.prefetch_related('questions__answers').get(id=page_id)
    except QuestionPage.DoesNotExist:
        return Response({'error': 'QuestionPage not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = QuestionPageDetailSerializer(question_page)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['delete'])
def delete_guest_game_session(request, game_session_id):
    try:
        game_session = GameSession.objects.get(id=game_session_id)
    except GameSession.DoesNotExist:
        return Response({'error': 'GameSession not found'}, status=status.HTTP_404_NOT_FOUND)

    if game_session.user is not None:
        return Response({'error': 'Only guest sessions can be deleted with this endpoint'}, status=status.HTTP_400_BAD_REQUEST)

    game_session.delete()
    return Response({'message': 'Guest game session deleted successfully'}, status=status.HTTP_200_OK)

@api_view(['post']) 
@permission_classes([IsAuthenticated])
def display_and_update_performance(request): 
    scholar = Scholar.objects.get(id=request.user.id)
    performance = scholar.performance 
    game_session = scholar.game_session
    try: 
        quiz_plan = game_session.quiz_plan
    except QuizPlan.DoesNotExist:
        return Response({'error': 'quiz plan doesnt exists!'}, status=status.HTTP_404_NOT_FOUND) 
    attempted = game_session.current_index * 10 
    correct = game_session.correct_answers
    experience = performance.experience 
    experience += attempted * 10 
    experience += correct * 30 
    leveled_up = False 
    if experience > 1000: 
        performance.level += 1 
        experience %= 1000
        leveled_up = True  
    performance.experience = experience 
    performance.attempted += attempted 
    performance.correct += correct 
    performance.save()
    data = {
        'experience': experience, 
        'attempted': attempted, 
        'correct_answers': correct, 
        'level': performance.level, 
    }
    game_session.delete()

    serializer = PerformanceSerializer(data)
    return Response(serializer.data, status=status.HTTP_201_CREATED)