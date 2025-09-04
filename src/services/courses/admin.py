from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import xlsxwriter
import io
from .models import Course, Instructor, CurriculumSection, Lesson, Enrollment, PricingPlan


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'title', 'courses_count', 'total_students', 'is_active', 'image_preview')
    list_filter = ('title', 'is_active')
    search_fields = ('name', 'title', 'bio', 'email')
    readonly_fields = ('image_preview', 'last_login', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'title', 'bio', 'image', 'image_preview')
        }),
        ('Authentication', {
            'fields': ('email', 'password', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Hash password if it's being set or changed
        if 'password' in form.changed_data or not change:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)
    
    def courses_count(self, obj):
        return obj.courses.count()
    courses_count.short_description = 'Courses'
    
    def total_students(self, obj):
        return Enrollment.objects.filter(course__instructor=obj).count()
    total_students.short_description = 'Total Students'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 50%;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'lessons_count', 'enrollment_count', 'revenue', 'image_preview')
    list_filter = ('instructor', 'is_trial_available')
    search_fields = ('title', 'description', 'overview')
    readonly_fields = ('image_preview', 'enrollment_count', 'revenue')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'image', 'image_preview', 'description', 'overview')
        }),
        ('Pricing & Lessons', {
            'fields': ('price', 'lessons_count')
        }),
        ('Instructor & Trial', {
            'fields': ('instructor', 'is_trial_available', 'trial_days')
        }),
    )
    
    def enrollment_count(self, obj):
        return obj.enrollment_set.count()
    enrollment_count.short_description = 'Enrollments'
    
    def revenue(self, obj):
        try:
            price_value = float(str(obj.price).replace('$','').strip())
        except (TypeError, ValueError):
            price_value = 0.0
        total = obj.enrollment_set.count() * price_value
        return f"${total:.2f}"
    revenue.short_description = 'Revenue'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px; border-radius: 8px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_on', 'is_trial', 'trial_status', 'days_enrolled')
    list_filter = ('is_trial', 'enrolled_on', 'course__instructor')
    search_fields = ('user__username', 'user__email', 'course__title')
    readonly_fields = ('days_enrolled', 'trial_status')
    date_hierarchy = 'enrolled_on'
    
    def trial_status(self, obj):
        if obj.is_trial:
            if obj.trial_expired:
                return format_html('<span style="color: red;">Expired</span>')
            else:
                return format_html('<span style="color: green;">Active</span>')
        return "Full Course"
    trial_status.short_description = 'Trial Status'
    
    def days_enrolled(self, obj):
        days = (timezone.now() - obj.enrolled_on).days
        return f"{days} days"
    days_enrolled.short_description = 'Days Enrolled'


@admin.register(CurriculumSection)
class CurriculumSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'lessons_count')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    
    def lessons_count(self, obj):
        return obj.lessons.count()
    lessons_count.short_description = 'Lessons'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'course', 'is_preview_available')
    list_filter = ('is_preview_available', 'section__course')
    search_fields = ('title', 'content', 'section__title')
    
    def course(self, obj):
        return obj.section.course.title
    course.short_description = 'Course'


class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'currency', 'billing_period', 'classes_per_week', 'classes_per_month', 'students_enrolled', 'is_popular', 'is_active']
    list_filter = ['is_active', 'is_popular', 'billing_period', 'currency']
    list_editable = ['price', 'students_enrolled', 'is_popular', 'is_active']
    search_fields = ['name']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'price', 'currency', 'billing_period', 'is_active')
        }),
        ('Class Details', {
            'fields': ('classes_per_week', 'classes_per_month', 'students_enrolled')
        }),
        ('Pricing Options', {
            'fields': ('is_popular', 'six_month_price', 'six_month_discount', 'twelve_month_price', 'twelve_month_discount')
        }),
    )


# Custom Admin Site for Dashboard
class CoursesAdminSite(admin.AdminSite):
    site_header = "Quran Learning - Course Management"
    site_title = "Course Admin"
    index_title = "Course Management Dashboard"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='courses_dashboard'),
            path('export-excel/', self.admin_view(self.export_excel), name='export_excel'),
            path('statistics/', self.admin_view(self.statistics_view), name='statistics'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        # Get statistics
        total_courses = Course.objects.count()
        total_instructors = Instructor.objects.count()
        total_enrollments = Enrollment.objects.count()
        def parse_price(p):
            try:
                return float(str(p).replace('$','').strip())
            except (TypeError, ValueError):
                return 0.0
        total_revenue = sum(parse_price(course.price) * course.enrollment_set.count() for course in Course.objects.all())
        
        # Recent enrollments
        recent_enrollments = Enrollment.objects.select_related('user', 'course').order_by('-enrolled_on')[:10]
        
        # Top courses by enrollment
        top_courses = Course.objects.annotate(
            enrollment_count=Count('enrollment')
        ).order_by('-enrollment_count')[:5]
        
        # Monthly enrollment trend
        current_month = timezone.now().month
        current_year = timezone.now().year
        monthly_enrollments = Enrollment.objects.filter(
            enrolled_on__year=current_year,
            enrolled_on__month=current_month
        ).count()
        
        # Trial vs Full enrollments
        trial_enrollments = Enrollment.objects.filter(is_trial=True).count()
        full_enrollments = Enrollment.objects.filter(is_trial=False).count()
        
        context = {
            'total_courses': total_courses,
            'total_instructors': total_instructors,
            'total_enrollments': total_enrollments,
            'total_revenue': total_revenue,
            'recent_enrollments': recent_enrollments,
            'top_courses': top_courses,
            'monthly_enrollments': monthly_enrollments,
            'trial_enrollments': trial_enrollments,
            'full_enrollments': full_enrollments,
        }
        
        return render(request, 'admin/courses/dashboard.html', context)
    
    def export_excel(self, request):
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        
        # Add formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4CAF50',
            'font_color': 'white',
            'border': 1
        })
        
        # Courses Sheet
        courses_sheet = workbook.add_worksheet('Courses')
        courses_data = Course.objects.select_related('instructor').all()
        
        # Headers
        headers = ['Title', 'Instructor', 'Price', 'Lessons', 'Enrollments', 'Revenue']
        for col, header in enumerate(headers):
            courses_sheet.write(0, col, header, header_format)
        
        # Data
        for row, course in enumerate(courses_data, 1):
            enrollment_count = course.enrollment_set.count()
            revenue = enrollment_count * course.price
            courses_sheet.write(row, 0, course.title)
            courses_sheet.write(row, 1, course.instructor.name)
            # Write price as string; also try numeric for safety
            courses_sheet.write(row, 2, str(course.price))
            courses_sheet.write(row, 3, course.lessons_count)
            courses_sheet.write(row, 4, enrollment_count)
            courses_sheet.write(row, 5, float(revenue))
        
        # Enrollments Sheet
        enrollments_sheet = workbook.add_worksheet('Enrollments')
        enrollments_data = Enrollment.objects.select_related('user', 'course').all()
        
        # Headers
        headers = ['Student', 'Email', 'Course', 'Enrolled Date', 'Trial', 'Days Enrolled']
        for col, header in enumerate(headers):
            enrollments_sheet.write(0, col, header, header_format)
        
        # Data
        for row, enrollment in enumerate(enrollments_data, 1):
            days_enrolled = (timezone.now() - enrollment.enrolled_on).days
            enrollments_sheet.write(row, 0, enrollment.user.username)
            enrollments_sheet.write(row, 1, enrollment.user.email)
            enrollments_sheet.write(row, 2, enrollment.course.title)
            enrollments_sheet.write(row, 3, enrollment.enrolled_on.strftime('%Y-%m-%d'))
            enrollments_sheet.write(row, 4, 'Yes' if enrollment.is_trial else 'No')
            enrollments_sheet.write(row, 5, days_enrolled)
        
        # Statistics Sheet
        stats_sheet = workbook.add_worksheet('Statistics')
        
        # Calculate statistics
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        total_revenue = sum(parse_price(course.price) * course.enrollment_set.count() for course in Course.objects.all())
        trial_enrollments = Enrollment.objects.filter(is_trial=True).count()
        full_enrollments = Enrollment.objects.filter(is_trial=False).count()
        
        stats_data = [
            ['Metric', 'Value'],
            ['Total Courses', total_courses],
            ['Total Enrollments', total_enrollments],
            ['Total Revenue', f"${total_revenue:.2f}"],
            ['Trial Enrollments', trial_enrollments],
            ['Full Enrollments', full_enrollments],
            ['Average Revenue per Course', f"${total_revenue/total_courses:.2f}" if total_courses > 0 else "$0.00"],
        ]
        
        for row, (metric, value) in enumerate(stats_data):
            if row == 0:
                enrollments_sheet.write(row, 0, metric, header_format)
                enrollments_sheet.write(row, 1, value, header_format)
            else:
                enrollments_sheet.write(row, 0, metric)
                enrollments_sheet.write(row, 1, value)
        
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="courses_report.xlsx"'
        return response
    
    def statistics_view(self, request):
        # Detailed statistics
        context = {
            'course_stats': self.get_course_statistics(),
            'enrollment_stats': self.get_enrollment_statistics(),
            'revenue_stats': self.get_revenue_statistics(),
            'instructor_stats': self.get_instructor_statistics(),
        }
        return render(request, 'admin/courses/statistics.html', context)
    
    def get_course_statistics(self):
        return {
            'total_courses': Course.objects.count(),
            'active_courses': Course.objects.filter(enrollment__isnull=False).distinct().count(),
            'avg_price': 0,  # price is string now; skip DB average
            'total_lessons': sum(course.lessons_count for course in Course.objects.all()),
        }
    
    def get_enrollment_statistics(self):
        return {
            'total_enrollments': Enrollment.objects.count(),
            'trial_enrollments': Enrollment.objects.filter(is_trial=True).count(),
            'full_enrollments': Enrollment.objects.filter(is_trial=False).count(),
            'this_month': Enrollment.objects.filter(
                enrolled_on__month=timezone.now().month
            ).count(),
        }
    
    def get_revenue_statistics(self):
        total_revenue = sum(parse_price(course.price) * course.enrollment_set.count() for course in Course.objects.all())
        return {
            'total_revenue': total_revenue,
            'avg_revenue_per_course': total_revenue / Course.objects.count() if Course.objects.count() > 0 else 0,
            'trial_revenue': 0,  # Trials are free
            'full_revenue': total_revenue,
        }
    
    def get_instructor_statistics(self):
        return {
            'total_instructors': Instructor.objects.count(),
            'active_instructors': Instructor.objects.filter(courses__isnull=False).distinct().count(),
            'avg_courses_per_instructor': Course.objects.count() / Instructor.objects.count() if Instructor.objects.count() > 0 else 0,
        }


# Register with custom admin site
courses_admin_site = CoursesAdminSite(name='courses_admin')
courses_admin_site.register(Course, CourseAdmin)
courses_admin_site.register(Instructor, InstructorAdmin)
courses_admin_site.register(Enrollment, EnrollmentAdmin)
courses_admin_site.register(CurriculumSection, CurriculumSectionAdmin)
courses_admin_site.register(Lesson, LessonAdmin)
courses_admin_site.register(PricingPlan, PricingPlanAdmin)
