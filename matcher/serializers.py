from rest_framework import serializers
from .models import CandidateProfile, JobPosting, JobMatch

class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = '__all__'

class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = '__all__'

class JobMatchSerializer(serializers.ModelSerializer):
    candidate = serializers.PrimaryKeyRelatedField(queryset=CandidateProfile.objects.all())
    job = serializers.PrimaryKeyRelatedField(queryset=JobPosting.objects.all())
    match_score = serializers.IntegerField()
    missing_skills = serializers.ListField(child=serializers.CharField())
    summary = serializers.CharField()

    class Meta:
        model = JobMatch
        fields = ['id', 'candidate', 'job', 'match_score', 'missing_skills', 'summary'] 