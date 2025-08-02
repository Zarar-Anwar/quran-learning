from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from src.core.filters import VideoFilter
from src.core.forms import ContactMessageForm
from src.core.models import Service, GalleryImage, Testimonial, Video
from src.services.courses.models import Course, Instructor
from .forms import UserProfileForm, ChangePasswordForm


# Create your views here.

class HomeView(TemplateView):
    template_name = "website/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.all()
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

class ScholarsView(TemplateView):
    template_name = "website/scholars.html"


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = "website/profile.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = UserProfileForm(instance=self.request.user)
        context['password_form'] = ChangePasswordForm()
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
