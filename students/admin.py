from django.contrib import admin
from .models import Student, CourseRegistration, Result

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('matric_no', 'user', 'department', 'level', 'date_joined')
    list_filter = ('department', 'level')
    search_fields = ('matric_no', 'user__username', 'user__first_name', 'user__last_name')


@admin.register(CourseRegistration)
class CourseRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'session', 'semester', 'date_registered')
    list_filter = ('session', 'semester', 'course__department')
    search_fields = ('student__matric_no', 'course__code')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('registration', 'score', 'grade', 'status', 'submitted_by', 'approved_by')
    list_filter = ('status', 'registration__semester', 'registration__session')
    search_fields = ('registration__student__matric_no', 'registration__course__code')
