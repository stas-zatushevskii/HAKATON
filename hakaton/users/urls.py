from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('generate-plan/', views.generate_learning_plan, name='generate_learning_plan'),
    path('test-plan/', views.test_learning_plan_view, name='test_learning_plan'),
] 