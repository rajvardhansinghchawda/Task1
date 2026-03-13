from django import forms
from .models import AvailabilitySlot, Doctor
from datetime import time

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['profile_photo', 'phone_number', 'gender', 'date_of_birth', 
                  'specialization', 'qualification', 'experience', 'license_number', 
                  'hospital_name', 'about', 'consultation_fee', 'available_from',
                  'available_to', 'default_slot_duration']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'available_from': forms.TimeInput(attrs={'type': 'time'}),
            'available_to': forms.TimeInput(attrs={'type': 'time'}),
        }

class SlotGeneratorForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': True})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': True})
    )
    
    DURATION_CHOICES = [
        (10, '10 Minutes'),
        (15, '15 Minutes'),
        (30, '30 Minutes'),
        (60, '1 Hour'),
    ]
    slot_duration_minutes = forms.ChoiceField(
        choices=DURATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        initial=15
    )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("End time must be after start time.")
            
        return cleaned_data
