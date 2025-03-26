from django.contrib import admin
from .models import CandidateProfile, JobPosting, JobMatch

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company')
    search_fields = ('title', 'company')

@admin.register(JobMatch)
class JobMatchAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'match_score')
    list_filter = ('match_score',)
    search_fields = ('candidate__name', 'job__title')
