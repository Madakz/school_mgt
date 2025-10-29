from django.contrib import admin
from .models import AdminUser, Report

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'can_approve_results', 'can_manage_users')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('department', 'total_students', 'total_courses', 'total_lecturers', 'generated_on')
    list_filter = ('department',)
    date_hierarchy = 'generated_on'
