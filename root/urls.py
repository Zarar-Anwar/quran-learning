from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.static import serve

from root.settings import ENVIRONMENT, MEDIA_ROOT, STATIC_ROOT
from src.core.handlers import (
    handler404, handler500
)
from src.services.courses.admin import courses_admin_site

urlpatterns = []

""" HANDLERS ------------------------------------------------------------------------------------------------------- """
handler404 = handler404
handler500 = handler500


""" INTERNAL REQUIRED APPS ----------------------------------------------------------------------------------------- """
urlpatterns += [
    path('', include('src.web.urls')),
    # path('api/', include('src.api.urls')),
]


""" EXTERNAL REQUIRED APPS ----------------------------------------------------------------------------------------- """
urlpatterns += [
    path('admin/', admin.site.urls),
    path('courses-admin/', courses_admin_site.urls),
    path('accounts/', include('allauth.urls')),
    path('courses/', include('src.services.courses.urls', namespace='courses')),
]


""" STATIC AND MEDIA FILES ----------------------------------------------------------------------------------------- """
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),
]


""" DEVELOPMENT ONLY -------------------------------------------------------------------------------------------- """
if ENVIRONMENT != 'server':
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls"))
    ]

    urlpatterns += [
        path('', TemplateView.as_view(template_name='dev/starter-page.html')),  # use: for home page/remove this
    ]
