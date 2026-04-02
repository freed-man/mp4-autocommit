from django import forms
from .models import ContactRequest


class ContactForm(forms.ModelForm):
    """Form for contact page submissions."""
    class Meta:
        model = ContactRequest
        fields = ('name', 'email', 'category', 'message')

    def __init__(self, *args, **kwargs):
        read_only_user = kwargs.pop('read_only_user', False)
        super().__init__(*args, **kwargs)
        if read_only_user:
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['name'].widget.attrs['class'] = 'form-control bg-light'
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['class'] = 'form-control bg-light'