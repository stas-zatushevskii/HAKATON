from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Challenge
from django.contrib.auth.decorators import login_required

@login_required
def challenge_list(request):
    """View to display all challenges with filtering and pagination"""
    challenges = Challenge.objects.filter(status='active')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        challenges = challenges.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Filter by difficulty
    difficulty_filter = request.GET.get('difficulty')
    if difficulty_filter:
        challenges = challenges.filter(difficulty=difficulty_filter)
    
    # Pagination
    paginator = Paginator(challenges, 12)  # Show 12 challenges per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get user's submissions for completed challenges
    user_submissions = {}
    if request.user.is_authenticated:
        from .models import Submission
        submissions = Submission.objects.filter(
            user=request.user,
            challenge__in=page_obj.object_list,
            is_best=True
        ).select_related('challenge')
        
        user_submissions = {
            submission.challenge.id: submission 
            for submission in submissions
        }
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'difficulty_filter': difficulty_filter,
        'difficulties': Challenge.DIFFICULTY_CHOICES,
        'user_submissions': user_submissions,
    }
    
    return render(request, 'tasks/challenge_list.html', context)

def challenge_detail(request, pk):
    """View to display a single challenge"""
    challenge = get_object_or_404(Challenge, pk=pk, status='active')
    
    # Get user's best submission for this challenge if authenticated
    best_submission = None
    if request.user.is_authenticated:
        from .models import Submission
        best_submission = Submission.objects.filter(
            user=request.user, 
            challenge=challenge, 
            is_best=True
        ).first()
    
    context = {
        'challenge': challenge,
        'best_submission': best_submission,
    }
    
    return render(request, 'tasks/challenge_detail.html', context) 