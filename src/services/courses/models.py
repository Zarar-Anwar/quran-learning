from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password, check_password

from src.services.users.models import User

class Instructor(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='instructors/')
    title = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    
    # Authentication fields
    email = models.EmailField(unique=True, help_text="Instructor's email for login")
    password = models.CharField(max_length=128, help_text="Instructor's password (will be hashed automatically)")
    is_active = models.BooleanField(default=True, help_text="Whether the instructor can login")
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Hash password if it's not already hashed
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def check_password(self, raw_password):
        """Check if the given password is correct"""
        return check_password(raw_password, self.password)
    
    def set_password(self, raw_password):
        """Set the password to a hashed version"""
        self.password = make_password(raw_password)
        self.save()
    
    def get_courses_count(self):
        return self.courses.count()
    
    def get_total_students(self):
        return Enrollment.objects.filter(course__instructor=self).count()
    
    def get_active_students(self):
        return Enrollment.objects.filter(course__instructor=self, is_trial=False).count()
    
    def get_trial_students(self):
        return Enrollment.objects.filter(course__instructor=self, is_trial=True).count()


class Course(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='courses/')
    description = models.TextField()
    overview = models.TextField()
    price = models.CharField(max_length=50)
    lessons_count = models.PositiveIntegerField()
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
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


class PricingPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    billing_period = models.CharField(max_length=20, default='monthly')  # monthly, yearly, etc.
    classes_per_week = models.PositiveIntegerField()
    classes_per_month = models.PositiveIntegerField()
    students_enrolled = models.PositiveIntegerField(default=0)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Discount information
    six_month_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    six_month_discount = models.PositiveIntegerField(default=7, help_text="Discount percentage for 6 months")
    twelve_month_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    twelve_month_discount = models.PositiveIntegerField(default=10, help_text="Discount percentage for 12 months")
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_period}"
    
    def get_six_month_price(self):
        """Calculate 6-month price with discount"""
        if self.six_month_price:
            return self.six_month_price
        from decimal import Decimal
        total = self.price * Decimal('6')
        discount = total * (Decimal(self.six_month_discount) / Decimal('100'))
        return total - discount
    
    def get_twelve_month_price(self):
        """Calculate 12-month price with discount"""
        if self.twelve_month_price:
            return self.twelve_month_price
        from decimal import Decimal
        total = self.price * Decimal('12')
        discount = total * (Decimal(self.twelve_month_discount) / Decimal('100'))
        return total - discount
