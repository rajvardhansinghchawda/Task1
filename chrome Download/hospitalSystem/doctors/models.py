from django.db import models
from django.conf import settings

class Doctor(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    
    # Basic Information
    profile_photo = models.ImageField(upload_to='doctor_photos/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Professional Information
    specialization = models.CharField(max_length=150)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    experience = models.PositiveIntegerField(help_text="Years of experience", default=0)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    hospital_name = models.CharField(max_length=255)

    # Additional Information
    about = models.TextField(blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Availability Preferences
    available_from = models.TimeField(blank=True, null=True)
    available_to = models.TimeField(blank=True, null=True)
    default_slot_duration = models.PositiveIntegerField(default=15, help_text="Default slot duration in minutes")

    def __str__(self):
        return f"Dr. {self.user.name} - {self.specialization}"

class AvailabilitySlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.doctor.user.name}: {self.date} {self.start_time}-{self.end_time}"
