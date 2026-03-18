from django.urls import path, include
from .views import * 
urlpatterns = [
    path('enter_page/', EnterPage.as_view(), name='enter_page'), 
    path('view_page/<str:year>/', ViewPage.as_view(), name='view_page'), 
    path('delete_page/<str:year>/', DeletePage.as_view(), name='delete_page'), 
]
