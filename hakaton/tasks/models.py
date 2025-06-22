from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Challenge(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_challenges')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Challenge specific fields
    time_limit = models.IntegerField(help_text="Time limit in minutes", default=60)
    memory_limit = models.IntegerField(help_text="Memory limit in MB", default=256)
    
    # Input/Output examples
    sample_input = models.TextField(blank=True, help_text="Sample input for the problem")
    sample_output = models.TextField(blank=True, help_text="Expected output for the sample input")
    
    # Additional details
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    points = models.IntegerField(default=100, help_text="Points awarded for solving this challenge")
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('challenge_detail', kwargs={'pk': self.pk})
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()] if self.tags else []


class Submission(models.Model):
    STATUS_CHOICES = [
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('partial', 'Partial'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    solution_code = models.TextField()
    programming_language = models.CharField(max_length=20, default='python')
    
    # Evaluation results
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    score = models.IntegerField(help_text="Score/Grade out of 100")
    
    # Detailed feedback
    overall_feedback = models.TextField(blank=True)
    correctness_feedback = models.TextField(blank=True)
    code_quality_feedback = models.TextField(blank=True)
    improvements = models.JSONField(default=list, blank=True)
    positive_points = models.JSONField(default=list, blank=True)
    test_results = models.JSONField(default=list, blank=True)
    next_steps = models.JSONField(default=list, blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Track if this is the user's best submission for this challenge
    is_best = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.score}/100)"
    
    def save(self, *args, **kwargs):
        # Ensure score is within valid range (0-100)
        if self.score < 0:
            self.score = 0
        elif self.score > 100:
            self.score = 100
        
        super().save(*args, **kwargs)
        
        # After saving, determine the best submission and update flags accordingly.
        # This ensures that 'is_best' is always correct, even when scores are updated.
        best_submission = Submission.objects.filter(
            user=self.user, challenge=self.challenge
        ).order_by('-score', '-submitted_at').first()

        if best_submission:
            # Set is_best to False for all other submissions for this user/challenge combination.
            # Using .update() avoids triggering the save() method again.
            Submission.objects.filter(
                user=self.user, challenge=self.challenge, is_best=True
            ).exclude(pk=best_submission.pk).update(is_best=False)

            # Set is_best to True for the top submission.
            if not best_submission.is_best:
                 Submission.objects.filter(pk=best_submission.pk).update(is_best=True) 