from django import forms
from .models import ContactMessage

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Full Name',
                'required': '',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your Email',
                'required': '',
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Type your Message',
                'required': '',
            }),
        }
