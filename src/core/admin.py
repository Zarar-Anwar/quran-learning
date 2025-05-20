from django.contrib import admin

from .models import (
    Country, Application, GalleryImage, Service, ContactMessage, Testimonial, Video
)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'tagline', 'is_active', 'created_on')


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'language', 'currency', 'phone_code', 'is_active', 'created_on')


admin.site.register(GalleryImage)
admin.site.register(Service)
admin.site.register(ContactMessage)
admin.site.register(Testimonial)
admin.site.register(Video)
