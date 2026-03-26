from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Form for users to update their profile."""
    class Meta:
        model = UserProfile
        fields = ('default_phone_number', 'default_email')