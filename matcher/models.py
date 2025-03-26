# matcher/models.py
from django.db import models

class CandidateProfile(models.Model):
    name = models.CharField(max_length=255)
    skills = models.JSONField()  # Store skills as a list of strings
    education = models.JSONField()  # Store education details as a list of dictionaries
    work_experience = models.JSONField()  # Store work experience as a list of dictionaries

    def __str__(self):
        return self.name

class JobPosting(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    required_skills = models.JSONField()  # Store required skills as a list of strings
    description = models.TextField()

    def __str__(self):
        return f"{self.title} at {self.company}"

class JobMatch(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    match_score = models.IntegerField()
    missing_skills = models.JSONField()  # Store missing skills as a list of strings
    summary = models.TextField()

    def __str__(self):
        return f"Match: {self.candidate} - {self.job} ({self.match_score})"