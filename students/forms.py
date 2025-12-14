# apps/students/forms.py
from django import forms
from .models import Result
from accounts.models import CustomUser

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['score', 'grade']
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
        }



class StudentProfileForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password (optional)'}),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Form styling
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")


    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # only update password if new one entered
        if commit:
            user.save()
        return user