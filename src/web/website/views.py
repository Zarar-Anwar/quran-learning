from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.

class HomeView(TemplateView):
    template_name = "website/home.html"

class ContactView(TemplateView):
    template_name = "website/contact.html"

class AboutView(TemplateView):
    template_name = "website/about.html"

class CoursesView(TemplateView):
    template_name = "website/courses.html"

class ServicesView(TemplateView):
    template_name = "website/services.html"

class BlogsView(TemplateView):
    template_name = "website/blogs.html"

class ScholarsView(TemplateView):
    template_name = "website/scholars.html"

