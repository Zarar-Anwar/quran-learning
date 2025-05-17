from django.contrib import admin
from .models import Course, Instructor, CurriculumSection, Lesson, Enrollment

admin.site.register(Instructor)
admin.site.register(Course)
admin.site.register(CurriculumSection)
admin.site.register(Lesson)
admin.site.register(Enrollment)
