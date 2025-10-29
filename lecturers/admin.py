from django.contrib import admin
from .models import Lecturer

@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'user', 'department', 'rank')
    list_filter = ('department',)
    search_fields = ('staff_id', 'user__username', 'user__first_name', 'user__last_name')
