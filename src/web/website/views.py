from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, FormView

from src.core.filters import VideoFilter
from src.core.forms import ContactMessageForm
from src.core.models import Service, GalleryImage, Testimonial, Video
from src.services.courses.models import Course, Instructor


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
