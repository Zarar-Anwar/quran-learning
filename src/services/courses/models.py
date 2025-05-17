from django.db import models
from django.utils import timezone
from datetime import timedelta

from src.services.users.models import User

class Instructor(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='instructors/')
    title = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='courses/')
    description = models.TextField()
    overview = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration_weeks = models.PositiveIntegerField()
    lessons_count = models.PositiveIntegerField()
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='courses')
    is_trial_available = models.BooleanField(default=True)
    trial_days = models.PositiveIntegerField(default=3)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_on = models.DateTimeField(auto_now_add=True)
    is_trial = models.BooleanField(default=False)
    trial_started = models.DateTimeField(blank=True, null=True)

    @property
    def trial_expired(self):
        if self.is_trial and self.trial_started:
            return timezone.now() > self.trial_started + timedelta(days=self.course.trial_days)
        return False

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"


class CurriculumSection(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    section = models.ForeignKey(CurriculumSection, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_preview_available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.section.title} - {self.title}"
