from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import JSONField  # если используешь PostgreSQL


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class TaskType(models.Model):
    name = models.CharField(max_length=120)


class Task(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    task_type = models.ForeignKey(TaskType, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=120)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    solution = models.JSONField(default=dict)


class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ("pending", "Ожидает"),
        ("submitted", "Отправлено"),
        ("checked", "Проверено")
    ])
    submitted_at = models.DateTimeField(null=True, blank=True)
