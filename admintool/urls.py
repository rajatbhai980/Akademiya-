from django.urls import path, include
from .views import * 
urlpatterns = [
    path('enter_page/', EnterPage.as_view(), name='enter_page')  
]
