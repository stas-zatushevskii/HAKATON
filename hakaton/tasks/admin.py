from django.contrib import admin
from .models import Challenge, Submission

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'status', 'points', 'created_by', 'created_at']
    list_filter = ['difficulty', 'status', 'created_at']
    search_fields = ['title', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status')
        }),
        ('Challenge Details', {
            'fields': ('difficulty', 'points', 'time_limit', 'memory_limit')
        }),
        ('Sample Data', {
            'fields': ('sample_input', 'sample_output')
        }),
        ('Metadata', {
            'fields': ('tags', 'created_by', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'score', 'status', 'programming_language', 'is_best', 'submitted_at']
    list_filter = ['status', 'programming_language', 'is_best', 'submitted_at']
    search_fields = ['user__username', 'challenge__title']
    readonly_fields = ['submitted_at']
    ordering = ['-submitted_at'] 