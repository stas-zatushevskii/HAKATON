from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.challenge_list, name='challenge_list'),
    path('<int:pk>/', views.challenge_detail, name='challenge_detail'),
] 