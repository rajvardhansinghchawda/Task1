import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

# Setup the OAuth 2.0 Flow
if settings.DEBUG:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For local development over HTTP
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'  # Allow Google to return more scopes than requested

CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'client_secret.json')
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'openid',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
]

def get_google_auth_flow(request):
    redirect_uri = getattr(settings, 'GOOGLE_CALENDAR_REDIRECT_URI', None) or request.build_absolute_uri(
        reverse('oauth2callback')
    )
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    return flow

def _get_valid_credentials(user):
    """
    Build Credentials from the user's stored token and refresh if expired.
    Returns valid Credentials or None if the token is missing/unrecoverable.
    """
    token_info = user.google_calendar_token
    if not token_info:
        return None

    try:
        # Credentials.from_authorized_user_info requires 'refresh_token' to be present 
        # for offline access logic to work.
        if 'refresh_token' not in token_info:
            print(f"DEBUG: Refresh token missing for user {user.email}")
            return None
            
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        # Log active scopes to debug the 403 error
        print(f"DEBUG: Token for {user.email} has scopes: {creds.scopes}")
    except ValueError as e:
        print(f"Error loading Google credentials for {user.email}: {e}")
        return None

    # If the token is expired, try to refresh it
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Persist the refreshed token back to the database
            user.google_calendar_token = json.loads(creds.to_json())
            user.save(update_fields=['google_calendar_token'])
        except Exception as e:
            print(f"Failed to refresh Google token for {user.email}: {e}")
            return None

    if not creds or not creds.valid:
        return None

    return creds

def create_calendar_event(user, appointment, is_doctor=False):
    creds = _get_valid_credentials(user)
    if creds is None:
        return False

    service = build('calendar', 'v3', credentials=creds)

    from django.utils import timezone
    tz_name = timezone.get_current_timezone_name()
    start_dt = datetime.datetime.combine(appointment.slot.date, appointment.slot.start_time)
    start_dt = timezone.make_aware(start_dt)
    end_dt = datetime.datetime.combine(appointment.slot.date, appointment.slot.end_time)
    end_dt = timezone.make_aware(end_dt)

    # Dynamic Title
    if is_doctor:
        summary = f'Appointment with {appointment.patient.name}'
    else:
        summary = f'Appointment with Dr. {appointment.doctor.user.name}'

    event = {
        'summary': summary,
        'location': appointment.doctor.hospital_name,
        'description': f'Hospital Appointment. Doctor: Dr. {appointment.doctor.user.name}, Patient: {appointment.patient.name}',
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': tz_name,
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': tz_name,
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"DEBUG: Successfully created calendar event for {user.email}")
        return True
    except Exception as e:
        if "insufficientPermissions" in str(e):
            print(f"CRITICAL ERROR: Insufficient permissions for {user.email}. THE USER LIKELY DID NOT CHECK THE PERMISSION BOXES DURING GOOGLE CONSENT.")
        print(f"Error creating calendar event for {user.email}: {e}")
        return False
