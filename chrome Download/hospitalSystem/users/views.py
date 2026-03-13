from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import EmailAuthenticationForm, EmailSignupForm, OTPVerificationForm, RoleSelectionForm, PatientOnboardingForm
from doctors.models import Doctor
from notifications.email_service import send_otp_email, send_welcome_email
from .models import User, OTPVerification
import random
import string

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def email_signup(request):
    if request.method == 'POST':
        form = EmailSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = generate_otp()
            # Send the OTP via email service
            send_otp_email(email, otp)
            print(f"OTP for {email}: {otp}")  # Also print for local dev convenience
            
            OTPVerification.objects.create(email=email, otp=otp)
            request.session['signup_email'] = email
            return redirect('verify_otp')
    else:
        form = EmailSignupForm()
    return render(request, 'users/signup.html', {'form': form})

def verify_otp(request):
    email = request.session.get('signup_email')
    if not email:
        return redirect('email_signup')

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            # Check if OTP is valid
            valid_otp = OTPVerification.objects.filter(email=email, otp=otp).order_by('-created_at').first()
            if valid_otp and valid_otp.is_valid():
                # Get or create user
                user, created = User.objects.get_or_create(email=email)
                if created:
                    user.set_unusable_password()
                    # Send welcome email for new user
                    send_welcome_email(user.email, user.name)
                user.is_verified = True
                user.save()
                
                # Delete used OTP
                valid_otp.delete()
                
                # Log the user in
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                # redirect to role selection if they don't have a role
                if not user.role:
                    return redirect('select_role')
                return redirect('dashboard')
            else:
                form.add_error('otp', 'Invalid or expired OTP')
    else:
        form = OTPVerificationForm()
        
    return render(request, 'users/verify_otp.html', {'form': form})

@login_required
def select_role(request):
    if request.user.role:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            name = form.cleaned_data['name']
            request.user.role = role
            request.user.name = name
            request.user.save()
            
            if role == 'DOCTOR':
                return redirect('doctor_onboarding')
            elif role == 'PATIENT':
                return redirect('patient_onboarding')
    else:
        form = RoleSelectionForm(initial={'name': request.user.name})
        
    return render(request, 'users/select_role.html', {'form': form})

@login_required
def patient_onboarding(request):
    if request.user.role != 'PATIENT':
        return redirect('dashboard')
        
    if hasattr(request.user, 'patientprofile'):
        return redirect('patient_dashboard')
        
    if request.method == 'POST':
        form = PatientOnboardingForm(request.POST)
        if form.is_valid():
            patient_profile = form.save(commit=False)
            patient_profile.user = request.user
            patient_profile.save()
            return redirect('patient_dashboard')
    else:
        form = PatientOnboardingForm()
        
    return render(request, 'users/patient_onboarding.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    # fallback to GET for simplicity
    logout(request)
    return redirect('login')

def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.role:
        return redirect('select_role')
    if request.user.role == 'DOCTOR':
        if not hasattr(request.user, 'doctor_profile'):
            return redirect('doctor_onboarding')
        return redirect('doctor_dashboard')
    
    if not hasattr(request.user, 'patientprofile'):
         return redirect('patient_onboarding')
    return redirect('patient_dashboard')
