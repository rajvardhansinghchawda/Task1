from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
import datetime

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = (
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
    )
    
    # We remove the unused username field, set email as the primary login field
    username = None
    email = models.EmailField('email address', unique=True)
    name = models.CharField(max_length=255, blank=True, null=True) # made optional for initial google accounts
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    google_calendar_token = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

class OTPVerification(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # valid for 5 minutes
        expiration_time = self.created_at + datetime.timedelta(minutes=5)
        return timezone.now() <= expiration_time

    def __str__(self):
        return f"{self.email} - {self.otp}"

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)

    def __str__(self):
        return f"Patient: {self.user.name or self.user.email}"
