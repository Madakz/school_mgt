from django.db import models

# FACULTY MODEL
class Faculty(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Department MODEL
class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.faculty.name})"


# COURSE MODEL
class Course(models.Model):
    LEVEL_CHOICES = [
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
    ]

    code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200)
    credit_unit = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    assigned_lecturer = models.ForeignKey(
        'lecturers.Lecturer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_courses'
    )

    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='required_for'
    )
    pass_mark = models.PositiveIntegerField(default=40)
    # course type options to choose from
    COURSE_TYPE_CHOICES = [
        ('core', 'Core'),
        ('elective', 'Elective'),
    ]
    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES, default='core')

    offered_level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='100')

    def __str__(self):
        return f"{self.code} – {self.title}"
