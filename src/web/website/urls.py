from django.urls import path

from src.web.website.views import HomeView, AboutView, ContactView, CoursesView, ServicesView, ScholarsView, \
    CoursesDetailsView, VideoListView, ProfileView, enroll_course, my_courses

app_name = "website"
urlpatterns = [
    path('',HomeView.as_view() , name="home"),
    path('about/',AboutView.as_view() , name="about"),
    path('contact/',ContactView.as_view() , name="contact"),
    path('courses/',CoursesView.as_view() , name="courses"),
    path('courses-details/<int:pk>/', CoursesDetailsView.as_view(), name="courses-details"),
    path('services/',ServicesView.as_view() , name="services"),
    path('videos/',VideoListView.as_view() , name="videos"),
    path('scholars', ScholarsView.as_view() , name="scholars"),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('enroll-course/<int:course_id>/', enroll_course, name="enroll_course"),
    path('my-courses/', my_courses, name="my_courses"),
]
