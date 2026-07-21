from django.contrib.auth import forms
from .models import CustomUser

class CustomUserCreationForm(forms.UserCreationForm):
    class Meta(forms.UserCreationForm.Meta):
        model = CustomUser
        fields = ('phone', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'رمز عبور'
        self.fields['password2'].label = 'تکرار رمز عبور'

class CustomUserChangeForm(forms.UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('phone', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'is_superuser')