import requests
from django.conf import settings
from django.core.mail import EmailMessage

EMAIL_SERVICE_URL = getattr(
    settings,
    'EMAIL_SERVICE_URL',
    'http://localhost:3000/send-email',
)

def send_otp_email(email, otp):
    payload = {
        "type": "OTP_VERIFICATION",
        "email": email,
        "data": {
            "otp": otp
        }
    }
    try:
        print(f"DEBUG: Attempting to call email service at {EMAIL_SERVICE_URL} for {email}")
        response = requests.post(EMAIL_SERVICE_URL, json=payload, timeout=5)
        print(f"DEBUG: Email service response: {response.status_code}")
        if response.status_code == 200:
            return True
        print(f"Email service error ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error calling email service: {e}")
    # Fallback to Django email backend
    subject = "Your Hospital HMS Verification Code"
    body = f"Your OTP verification code is: {otp}\n\nThis code expires in 5 minutes."
    return _send_via_django_email_backend(subject, body, email)

def _send_via_django_email_backend(subject: str, body: str, recipient: str) -> bool:
    try:
        msg = EmailMessage(subject=subject, body=body, to=[recipient])
        sent_count = msg.send(fail_silently=False)
        return sent_count > 0
    except Exception as e:
        print(f"Error sending email via Django backend: {e}")
        return False

def send_welcome_email(user_email, user_name):
    payload = {
        "type": "SIGNUP_WELCOME",
        "email": user_email,
        "data": {
            "name": user_name
        }
    }
    try:
        response = requests.post(EMAIL_SERVICE_URL, json=payload, timeout=5)
        if response.status_code == 200:
            return True
        print(f"Email service error ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error calling email service: {e}")
    # Fallback to Django email backend if configured
    subject = "Welcome to Hospital HMS"
    body = f"Hello {user_name or 'User'},\n\nWelcome to our platform. We're glad to have you!"
    return _send_via_django_email_backend(subject, body, user_email)

def send_booking_confirmation(user_email, appointment):
    payload = {
        "type": "BOOKING_CONFIRMATION",
        "email": user_email,
        "data": {
            "doctor": f"Dr. {appointment.doctor.user.name}",
            "patient": appointment.patient.name,
            "date": str(appointment.slot.date),
            "time": f"{appointment.slot.start_time} - {appointment.slot.end_time}"
        }
    }
    try:
        response = requests.post(EMAIL_SERVICE_URL, json=payload, timeout=5)
        if response.status_code == 200:
            return True
        print(f"Email service error ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error calling email service: {e}")
    # Fallback to Django email backend if configured
    subject = "Appointment Confirmed"
    body = (
        f"Hello {appointment.patient.name},\n\n"
        f"Your appointment with Dr. {appointment.doctor.user.name} is confirmed.\n\n"
        f"Date: {appointment.slot.date}\n"
        f"Time: {appointment.slot.start_time} - {appointment.slot.end_time}\n\n"
        "Thank you,\n"
        "Mini Hospital Management System"
    )
    return _send_via_django_email_backend(subject, body, user_email)

def send_booking_notification_to_doctor(doctor_email, appointment):
    payload = {
        "type": "BOOKING_NOTIFICATION_DOCTOR",
        "email": doctor_email,
        "data": {
            "doctor": f"Dr. {appointment.doctor.user.name}",
            "patient": appointment.patient.name,
            "date": str(appointment.slot.date),
            "time": f"{appointment.slot.start_time} - {appointment.slot.end_time}"
        }
    }
    try:
        response = requests.post(EMAIL_SERVICE_URL, json=payload, timeout=5)
        if response.status_code == 200:
            return True
        print(f"Email service error ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error calling email service: {e}")
    # Fallback to Django email backend if configured
    subject = "New Appointment Booked"
    body = (
        f"Hello Dr. {appointment.doctor.user.name},\n\n"
        f"A new appointment has been booked by {appointment.patient.name}.\n\n"
        f"Date: {appointment.slot.date}\n"
        f"Time: {appointment.slot.start_time} - {appointment.slot.end_time}\n\n"
        "Thank you,\n"
        "Mini Hospital Management System"
    )
    return _send_via_django_email_backend(subject, body, doctor_email)
