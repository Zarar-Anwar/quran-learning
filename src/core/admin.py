from django.contrib import admin

from .models import (
    Country, Application, GalleryImage, Service, ContactMessage, Testimonial, Video
)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'tagline', 'whatsapp_number', 'is_active', 'created_on')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_name', 'tagline', 'description')
        }),
        ('Contact Information', {
            'fields': ('contact_email1', 'contact_email2', 'contact_phone1', 'contact_phone2', 'whatsapp_number')
        }),
        ('Media & Branding', {
            'fields': ('favicon', 'logo', 'logo_dark', 'logo_light')
        }),
        ('Location', {
            'fields': ('address', 'latitude', 'longitude')
        }),
        ('Settings', {
            'fields': ('terms_url', 'version', 'is_active')
        }),
    )


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'language', 'currency', 'phone_code', 'is_active', 'created_on')


admin.site.register(GalleryImage)
admin.site.register(Service)
admin.site.register(ContactMessage)
admin.site.register(Testimonial)
admin.site.register(Video)
