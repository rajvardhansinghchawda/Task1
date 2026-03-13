from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, PatientProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'role')

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'role')

class EmailAuthenticationForm(AuthenticationForm):
    """Override to show 'Email' label instead of 'Username'."""
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True})
    )

class EmailSignupForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'autofocus': True}))

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'placeholder': '6-digit OTP'}))

class RoleSelectionForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.RadioSelect)

class PatientOnboardingForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['phone_number', 'aadhar_number']
        
    def clean_aadhar_number(self):
        aadhar = self.cleaned_data.get('aadhar_number')
        if aadhar and (not aadhar.isdigit() or len(aadhar) != 12):
            raise forms.ValidationError('Aadhar number must be exactly 12 digits.')
        return aadhar
