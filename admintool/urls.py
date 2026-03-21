from django.urls import path, include
from .views import * 
urlpatterns = [
    path('enter_page/', EnterPage.as_view(), name='enter_page'),
    path('view_page/<str:year>/<int:subject_id>/', ViewPage.as_view(), name='view_page'),
    path('update_page/<str:year>/<int:subject_id>/', UpdatePage.as_view(), name='update_page'),
    path('delete_page/<str:year>/<int:subject_id>/', DeletePage.as_view(), name='delete_page'),
    path('semesters/', ViewSemesters.as_view(), name='view_semesters'),
    path('subjects/<int:semester_id>/', ViewSubjects.as_view(), name='view_subjects'),
]
