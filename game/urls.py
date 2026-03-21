from django.urls import path, include
from . import views

urlpatterns = [
    path('start/', views.StartGame.as_view(), name='start_game'),
    path('semesters/', views.view_semesters, name='view_semesters'),
    path('subjects/<int:semester_id>/', views.view_subjects, name='view_subjects'),
    path('pages_counts/', views.view_pages_counts, name='view_pages_counts' )
]