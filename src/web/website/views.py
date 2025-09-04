from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.hashers import check_password
from .forms import UserProfileForm, ChangePasswordForm
from src.services.users.models import User
from src.services.courses.models import Course, Enrollment, Instructor
from src.core.models import Service, GalleryImage, Testimonial, Application, Video
from src.core.filters import VideoFilter
from src.core.forms import ContactMessageForm
from src.services.courses.models import PricingPlan


# Create your views here.

class HomeView(TemplateView):
    template_name = "website/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.order_by('-id')[:6]
        context['services'] = Service.objects.order_by('-id')[:3]
        context['instructors'] = Instructor.objects.all()
        context['gallery'] = GalleryImage.objects.all()
        context["testimonials"] = Testimonial.objects.all()
        return context


class ContactView(FormView):
    template_name = "website/contact.html"
    form_class = ContactMessageForm
    success_url = reverse_lazy('website:contact')  # make sure this name matches your url

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your message has been sent successfully.")
        return super().form_valid(form)


class AboutView(TemplateView):
    template_name = "website/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instructors'] = Instructor.objects.all()
        context["testimonials"] = Testimonial.objects.all()
        return context



class CoursesView(ListView):
    model = Course
    template_name = "website/courses.html"
    context_object_name = 'courses'


class CoursesDetailsView(DetailView):
    model = Course
    template_name = "website/courses-details.html"
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_enrollment'] = Enrollment.objects.filter(
                user=self.request.user, 
                course=self.object
            ).first()
        return context


class ServicesView(ListView):
    model = Service
    template_name = "website/services.html"
    context_object_name = 'services'


class VideoListView(ListView):
    model = Video
    template_name = 'website/videos.html'
    context_object_name = 'videos'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        self.video_filter = VideoFilter(self.request.GET, queryset=queryset)
        return self.video_filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.video_filter
        return context


class PricingView(TemplateView):
    template_name = "website/pricing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pricing_plans'] = PricingPlan.objects.filter(is_active=True).order_by('price')
        return context

class ScholarsView(TemplateView):
    template_name = "website/scholars.html"


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = "website/profile.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = UserProfileForm(instance=self.request.user)
        context['password_form'] = ChangePasswordForm()
        # Add user's enrolled courses
        context['enrolled_courses'] = Enrollment.objects.filter(user=self.request.user).select_related('course', 'course__instructor')
        return context
    
    def post(self, request, *args, **kwargs):
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('website:profile')
            else:
                messages.error(request, 'Please correct the errors below.')
                context = self.get_context_data()
                context['profile_form'] = profile_form
                return self.render_to_response(context)
        
        elif 'change_password' in request.POST:
            password_form = ChangePasswordForm(request.POST)
            if password_form.is_valid():
                user = request.user
                if user.check_password(password_form.cleaned_data['current_password']):
                    user.set_password(password_form.cleaned_data['new_password1'])
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Password changed successfully!')
                    return redirect('website:profile')
                else:
                    messages.error(request, 'Current password is incorrect.')
                    context = self.get_context_data()
                    context['password_form'] = password_form
                    return self.render_to_response(context)
            else:
                messages.error(request, 'Please correct the errors below.')
                context = self.get_context_data()
                context['password_form'] = password_form
                return self.render_to_response(context)
        
        return redirect('website:profile')

@login_required
@require_POST
def enroll_course(request, course_id):
    """Enroll user in a course"""
    course = get_object_or_404(Course, id=course_id)
    user = request.user
    
    # Check if user is already enrolled
    if Enrollment.objects.filter(user=user, course=course).exists():
        messages.warning(request, f"You are already enrolled in {course.title}")
        return JsonResponse({'status': 'already_enrolled', 'message': 'Already enrolled'})
    
    # Create enrollment
    enrollment = Enrollment.objects.create(
        user=user,
        course=course,
        is_trial=course.is_trial_available,
        trial_started=timezone.now() if course.is_trial_available else None
    )
    
    messages.success(request, f"Successfully enrolled in {course.title}")
    return JsonResponse({'status': 'success', 'message': 'Enrollment successful'})

@login_required
def my_courses(request):
    """View for user's enrolled courses"""
    enrolled_courses = Enrollment.objects.filter(user=request.user).select_related('course', 'course__instructor')
    return render(request, 'website/my_courses.html', {
        'enrolled_courses': enrolled_courses
    })

def unified_login(request):
    """Unified login view for both students and instructors"""
    # Redirect if user is already logged in
    if request.user.is_authenticated:
        return redirect('website:home')
    
    # Redirect if instructor is already logged in
    if 'instructor_id' in request.session:
        return redirect('courses:instructor_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', 'student')
        
        if user_type == 'instructor':
            # Try instructor login
            try:
                instructor = Instructor.objects.get(email=email, is_active=True)
                if instructor.check_password(password):
                    # Update last login
                    instructor.last_login = timezone.now()
                    instructor.save()
                    
                    # Store instructor in session
                    request.session['instructor_id'] = instructor.id
                    request.session['instructor_name'] = instructor.name
                    request.session['user_type'] = 'instructor'
                    
                    messages.success(request, f'Welcome back, {instructor.name}!')
                    return redirect('courses:instructor_dashboard')
                else:
                    messages.error(request, 'Invalid password.')
            except Instructor.DoesNotExist:
                messages.error(request, 'Instructor not found or account is not active.')
        else:
            # Try student login - first try with email as username, then try to find user by email
            user = authenticate(request, username=email, password=password)
            if user is None:
                # Try to find user by email
                try:
                    user_obj = User.objects.get(email=email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('website:home')
            else:
                messages.error(request, 'Invalid credentials.')
    
    return render(request, 'website/unified_login.html')


def unified_logout(request):
    """Unified logout view"""
    user_type = request.session.get('user_type')
    
    if user_type == 'instructor':
        # Clear instructor session
        if 'instructor_id' in request.session:
            del request.session['instructor_id']
        if 'instructor_name' in request.session:
            del request.session['instructor_name']
        if 'user_type' in request.session:
            del request.session['user_type']
        messages.success(request, 'You have been logged out successfully.')
        return redirect('website:unified_login')
    else:
        # Student logout
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('website:home')
