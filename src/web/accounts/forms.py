from django.forms import ModelForm
from src.services.users.models import User


from allauth.account.forms import SignupForm
from django import forms

from allauth.account.forms import SignupForm
from django import forms

class CustomSignupForm(SignupForm):
    name = forms.CharField(
        max_length=150,
        label='Full Name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your phone number'})
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your country'})
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your city'})
    )
    user_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'You are interested to get the services for yourself, for your kids, or anyone else. Kindly write Name, Age and Gender of the student(s) interested for classes.',
            'rows': 4
        })
    )

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['name']
        user.phone_number = self.cleaned_data['phone_number']
        user.country = self.cleaned_data['country']
        user.city = self.cleaned_data['city']
        user.user_message = self.cleaned_data['user_message']
        user.save()
        return user



class UserProfileForm(ModelForm):

    class Meta:
        model = User
        fields = [
            'profile_image', 'first_name', 'last_name',
            'phone_number'
        ]


