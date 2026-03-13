from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.shortcuts import resolve_url
from notifications.email_service import send_welcome_email

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        if request.user.is_authenticated:
            if not request.user.role or request.user.role not in ['DOCTOR', 'PATIENT']:
                return resolve_url('select_role')
            if request.user.role == 'DOCTOR':
                if not hasattr(request.user, 'doctor_profile'):
                    return resolve_url('doctor_onboarding')
                return resolve_url('doctor_dashboard')
            elif request.user.role == 'PATIENT':
                if not hasattr(request.user, 'patientprofile'):
                    return resolve_url('patient_onboarding')
                return resolve_url('patient_dashboard')
        return super().get_login_redirect_url(request)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.is_verified = True # Social accounts are pre-verified via Google
        user.save()
        # Send welcome email for new social user
        send_welcome_email(user.email, user.name)
        return user
