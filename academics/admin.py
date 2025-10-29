from django.contrib import admin
from .models import Faculty, Department, Course

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'description')
    list_filter = ('faculty',)
    search_fields = ('name', 'faculty__name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'credit_unit', 'department', 'assigned_lecturer')
    list_filter = ('department',)
    search_fields = ('code', 'title')
