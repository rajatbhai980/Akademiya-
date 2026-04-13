from django.urls import path, include
from . import views

urlpatterns = [
    path('start/', views.StartGame.as_view(), name='start_game'),
    path('semesters/', views.view_semesters, name='view_semesters_user'),
    path('subjects/<int:semester_id>/', views.view_subjects, name='view_subjects_user'),
    path('pages_counts/', views.view_pages_counts, name='view_pages_counts_user'),
    path('submit_answer/', views.submit_answer, name='submit_answer'), 
    path('view_question_pages/<int:game_session_id>/', views.view_question_pages, name='view_question_pages'),
    path('view_question_page/<int:page_id>/', views.view_question_page_detail, name='view_question_page_detail'),
    path('delete_guest_session/<int:game_session_id>/', views.delete_guest_game_session, name='delete_guest_game_session'),
    path('display_and_update_performance/', views.display_and_update_performance, name='display_and_update_performance'),
]