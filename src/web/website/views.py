from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView

from src.services.courses.models import Course


# Create your views here.

class HomeView(TemplateView):
    template_name = "website/home.html"

class ContactView(TemplateView):
    template_name = "website/contact.html"

class AboutView(TemplateView):
    template_name = "website/about.html"

class CoursesView(ListView):
    model = Course
    template_name = "website/courses.html"
    context_object_name = 'courses'

class CoursesDetailsView(DetailView):
    model = Course
    template_name = "website/courses-details.html"
    context_object_name = 'course'

class ServicesView(TemplateView):
    template_name = "website/services.html"

class VideosView(TemplateView):
    template_name = "website/videos.html"

class ScholarsView(TemplateView):
    template_name = "website/scholars.html"

