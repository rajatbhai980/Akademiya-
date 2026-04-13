from django.urls import path
from . import views

urlpatterns = [
    path('subscription/', views.purchase_subscription, name='purchase_subscription'),
]