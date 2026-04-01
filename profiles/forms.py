from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Form for users to update their editable profile fields."""
    username = forms.CharField(max_length=150, required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = UserProfile
        fields = ('default_phone_number',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

        self.field_order = [
            'username', 'first_name', 'last_name', 'default_phone_number'
        ]
        self.order_fields(self.field_order)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        current_user = self.instance.user
        if User.objects.filter(username=username).exclude(
                pk=current_user.pk).exists():
            raise forms.ValidationError(
                'this username is already taken.'
            )
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.username = self.cleaned_data.get('username', user.username)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            profile.save()
        return profile