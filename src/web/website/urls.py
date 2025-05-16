from django.urls import path

from src.web.website.views import HomeView, AboutView, ContactView, CoursesView, ServicesView, BlogsView, ScholarsView

app_name = "website"
urlpatterns = [
    path('',HomeView.as_view() , name="home"),
    path('about/',AboutView.as_view() , name="about"),
    path('contact/',ContactView.as_view() , name="contact"),
    path('courses/',CoursesView.as_view() , name="courses"),
    path('services/',ServicesView.as_view() , name="services"),
    path('blogs/',BlogsView.as_view() , name="blogs"),
    path('scholars', ScholarsView.as_view() , name="scholars"),

]
