from django.db import models

class Faculty(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.faculty.name})"


# -----------------------------
# COURSE MODEL
# -----------------------------
class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200)
    credit_unit = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    assigned_lecturer = models.ForeignKey('lecturers.Lecturer', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_courses')

    def __str__(self):
        return f"{self.code} - {self.title}"
