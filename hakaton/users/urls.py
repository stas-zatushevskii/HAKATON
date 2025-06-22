from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('generate-plan/', views.generate_learning_plan, name='generate_learning_plan'),
    path('test-plan/', views.test_learning_plan_view, name='test_learning_plan'),
    path('process-answer/', views.process_user_answer, name='process_user_answer'),
    path('create-challenge/', views.create_challenge_from_plan, name='create_challenge'),
    path('evaluate-solution/', views.evaluate_solution, name='evaluate_solution'),
    path('challenge-creator/', views.challenge_creator_view, name='challenge_creator'),
    path('solution-evaluator/', views.solution_evaluator_view, name='solution_evaluator'),
] 