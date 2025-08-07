from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Instructor URLs
    path('instructor/login/', views.instructor_login, name='instructor_login'),
    path('instructor/logout/', views.instructor_logout, name='instructor_logout'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/courses/', views.instructor_courses, name='instructor_courses'),
    path('instructor/courses/<int:course_id>/', views.instructor_course_detail, name='instructor_course_detail'),
    path('instructor/students/', views.instructor_students, name='instructor_students'),
    path('instructor/profile/', views.instructor_profile, name='instructor_profile'),
]
