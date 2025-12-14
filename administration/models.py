from django.db import models
from academics.models import Department
from accounts.models import CustomUser


class AdminUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin_profile')
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Admin'),
        ('Academic Officer', 'Academic Officer'),
    ])
    can_approve_results = models.BooleanField(default=True)
    can_manage_users = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# -----------------------------
# STATISTICS / REPORTS
# -----------------------------
class Report(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    total_students = models.PositiveIntegerField(default=0)
    total_courses = models.PositiveIntegerField(default=0)
    total_lecturers = models.PositiveIntegerField(default=0)
    generated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.department.name} on {self.generated_on.date()}"
