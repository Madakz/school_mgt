from django import forms
from accounts.models import CustomUser
from .models import AdminUser
from lecturers.models import Lecturer
from students.models import Student, Result
from academics.models import Course

class AdminUserForm(forms.ModelForm):
    
    role_display = forms.CharField(
        label="User Type",
        initial="admin",
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
    )
    class Meta:
        model = AdminUser
        exclude = ['user']  # we’ll assign this in the view

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form styling
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")

            

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form styling
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")


class LecturerForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Lecturer
        fields = ['staff_id', 'department', 'rank']

    def __init__(self, *args, **kwargs):
        # Check if we're editing an existing Lecturer
        super().__init__(*args, **kwargs)

        # add boostrap class
        for field_name, field in self.fields.items():
            # Default to form-control for most inputs
            bootstrap_class = "form-control"
            
            # Set or append the class (use setdefault to avoid overwriting existing attrs)
            field.widget.attrs.setdefault("class", bootstrap_class)

        if self.instance and self.instance.pk:
            self.fields['email'].initial = self.instance.user.email
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        # Create or update the related CustomUser
        if self.instance.pk:
            user = self.instance.user
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']

            # Only change password if entered
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            user.save()
        else:
            user = CustomUser.objects.create_user(
                username=self.cleaned_data['email'],  # only if using AbstractUser
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                password=self.cleaned_data['password'],
                role='lecturer'
            )
            self.instance.user = user

        lecturer = super().save(commit=False)
        lecturer.user = user
        if commit:
            lecturer.save()
        return lecturer


class StudentForm(forms.ModelForm):
    email = forms.EmailField()
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Student
        fields = ['matric_no', 'department', 'level', 'admission_year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form styling
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        student = super().save(commit=False)
        data = self.cleaned_data

        if not student.user_id:
            # Create new user for student
            user = CustomUser.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                role='student'
            )
            student.user = user
        else:
            # Update existing linked user
            user = student.user
            user.username = data['username']
            user.email = data['email']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            if data['password']:
                user.set_password(data['password'])
            user.save()

        if commit:
            student.save()
        return student    



class CourseAssignmentForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'title', 'credit_unit', 'department', 'assigned_lecturer']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'credit_unit': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'assigned_lecturer': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_lecturer'].queryset = Lecturer.objects.all()


class ResultApprovalForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['score', 'grade', 'status']
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'grade': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
