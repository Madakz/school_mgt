from django.db import models
from accounts.models import CustomUser
from academics.models import Department

class Lecturer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='lecturer_profile')
    staff_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='lecturers')
    rank = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.staff_id} - {self.user.get_full_name()}"
