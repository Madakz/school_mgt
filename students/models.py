from django.db import models
from accounts.models import CustomUser
from academics.models import Department, Course
from lecturers.models import Lecturer

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    matric_no = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    level = models.CharField(max_length=10, choices=[
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
    ])
    admission_year = models.IntegerField(default=2025)

    def __str__(self):
        return f"{self.matric_no} - {self.user.get_full_name()}"



class CourseRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='registrations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='registrations')
    session = models.CharField(max_length=15)
    semester = models.CharField(max_length=10, choices=[('First', 'First'), ('Second', 'Second')])
    date_registered = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course', 'session', 'semester')

    def __str__(self):
        return f"{self.student.matric_no} - {self.course.code} ({self.session})"


# -----------------------------
# RESULTS MODEL
# -----------------------------
class Result(models.Model):
    registration = models.OneToOneField(CourseRegistration, on_delete=models.CASCADE, related_name='result')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved')], default='Pending')
    submitted_by = models.ForeignKey('lecturers.Lecturer', on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_results')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_results')

    def __str__(self):
        return f"{self.registration.student.matric_no} - {self.registration.course.code}"
