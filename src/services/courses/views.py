from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count, Q
from .models import Course, Enrollment, Instructor
from django.contrib.auth.hashers import make_password, check_password


def instructor_login(request):
    """Instructor login view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Find instructor by email
        try:
            instructor = Instructor.objects.get(email=email, is_active=True)
            
            # Check password
            if check_password(password, instructor.password):
                # Update last login
                instructor.last_login = timezone.now()
                instructor.save()
                
                # Store instructor in session
                request.session['instructor_id'] = instructor.id
                request.session['instructor_name'] = instructor.name
                
                messages.success(request, f'Welcome back, {instructor.name}!')
                return redirect('instructor_dashboard')
            else:
                messages.error(request, 'Invalid password.')
        except Instructor.DoesNotExist:
            messages.error(request, 'Instructor not found or account is not active.')
    
    return render(request, 'instructor/login.html')


def instructor_logout(request):
    """Instructor logout view"""
    # Clear instructor session
    if 'instructor_id' in request.session:
        del request.session['instructor_id']
    if 'instructor_name' in request.session:
        del request.session['instructor_name']
    if 'user_type' in request.session:
        del request.session['user_type']
    
    messages.success(request, 'You have been logged out successfully.')
    return redirect('website:unified_login')


def instructor_required(view_func):
    """Decorator to check if user is logged in as instructor"""
    def wrapper(request, *args, **kwargs):
        if 'instructor_id' not in request.session or request.session.get('user_type') != 'instructor':
            messages.error(request, 'Please log in to access this page.')
            return redirect('website:unified_login')
        return view_func(request, *args, **kwargs)
    return wrapper


@instructor_required
def instructor_dashboard(request):
    """Instructor dashboard view"""
    instructor_id = request.session['instructor_id']
    instructor = get_object_or_404(Instructor, id=instructor_id)
    
    # Get instructor's courses
    courses = Course.objects.filter(instructor=instructor)
    
    # Get enrollment statistics
    total_enrollments = Enrollment.objects.filter(course__instructor=instructor).count()
    trial_enrollments = Enrollment.objects.filter(course__instructor=instructor, is_trial=True).count()
    full_enrollments = Enrollment.objects.filter(course__instructor=instructor, is_trial=False).count()
    
    # Get recent enrollments
    recent_enrollments = Enrollment.objects.filter(
        course__instructor=instructor
    ).select_related('user', 'course').order_by('-enrolled_on')[:10]
    
    # Get top performing courses
    top_courses = courses.annotate(
        enrollment_count=Count('enrollment')
    ).order_by('-enrollment_count')[:5]
    
    # Calculate revenue
    total_revenue = sum(course.price * course.enrollment_set.count() for course in courses)
    
    context = {
        'instructor': instructor,
        'courses': courses,
        'total_courses': courses.count(),
        'total_enrollments': total_enrollments,
        'trial_enrollments': trial_enrollments,
        'full_enrollments': full_enrollments,
        'total_revenue': total_revenue,
        'recent_enrollments': recent_enrollments,
        'top_courses': top_courses,
    }
    
    return render(request, 'instructor/dashboard.html', context)


@instructor_required
def instructor_courses(request):
    """Instructor's courses view"""
    instructor_id = request.session['instructor_id']
    instructor = get_object_or_404(Instructor, id=instructor_id)
    
    courses = Course.objects.filter(instructor=instructor).annotate(
        enrollment_count=Count('enrollment')
    ).order_by('-id')
    
    context = {
        'instructor': instructor,
        'courses': courses,
    }
    
    return render(request, 'instructor/courses.html', context)


@instructor_required
def instructor_course_detail(request, course_id):
    """Instructor's course detail view"""
    instructor_id = request.session['instructor_id']
    instructor = get_object_or_404(Instructor, id=instructor_id)
    
    course = get_object_or_404(Course, id=course_id, instructor=instructor)
    
    # Get enrollments for this course
    enrollments = Enrollment.objects.filter(course=course).select_related('user').order_by('-enrolled_on')
    
    # Get statistics
    total_enrollments = enrollments.count()
    trial_enrollments = enrollments.filter(is_trial=True).count()
    full_enrollments = enrollments.filter(is_trial=False).count()
    revenue = course.price * total_enrollments
    
    context = {
        'instructor': instructor,
        'course': course,
        'enrollments': enrollments,
        'total_enrollments': total_enrollments,
        'trial_enrollments': trial_enrollments,
        'full_enrollments': full_enrollments,
        'revenue': revenue,
    }
    
    return render(request, 'instructor/course_detail.html', context)


@instructor_required
def instructor_students(request):
    """Instructor's students view"""
    instructor_id = request.session['instructor_id']
    instructor = get_object_or_404(Instructor, id=instructor_id)
    
    # Get all enrollments for instructor's courses
    enrollments = Enrollment.objects.filter(
        course__instructor=instructor
    ).select_related('user', 'course').order_by('-enrolled_on')
    
    # Filter by trial status if requested
    trial_filter = request.GET.get('trial')
    if trial_filter == 'true':
        enrollments = enrollments.filter(is_trial=True)
    elif trial_filter == 'false':
        enrollments = enrollments.filter(is_trial=False)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        enrollments = enrollments.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(course__title__icontains=search)
        )
    
    context = {
        'instructor': instructor,
        'enrollments': enrollments,
        'total_students': enrollments.count(),
        'trial_students': enrollments.filter(is_trial=True).count(),
        'full_students': enrollments.filter(is_trial=False).count(),
    }
    
    return render(request, 'instructor/students.html', context)


@instructor_required
def instructor_profile(request):
    """Instructor's profile view"""
    instructor_id = request.session['instructor_id']
    instructor = get_object_or_404(Instructor, id=instructor_id)
    
    if request.method == 'POST':
        # Handle profile update
        instructor.name = request.POST.get('name', instructor.name)
        instructor.title = request.POST.get('title', instructor.title)
        instructor.bio = request.POST.get('bio', instructor.bio)
        
        # Handle profile image
        if 'image' in request.FILES:
            instructor.image = request.FILES['image']
        
        instructor.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('instructor_profile')
    
    context = {
        'instructor': instructor,
    }
    
    return render(request, 'instructor/profile.html', context)
