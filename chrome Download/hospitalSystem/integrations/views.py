from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .google_calendar import get_google_auth_flow
from users.models import User
import json

@login_required
def google_calendar_init(request):
    """Initiates the Google OAuth2 flow"""
    try:
        flow = get_google_auth_flow(request)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            include_granted_scopes='true'
        )
        request.session['state'] = state
        request.session['code_verifier'] = flow.code_verifier  # Required for PKCE validation
        return redirect(authorization_url)
    except Exception as e:
        return render(request, 'integrations/oauth_error.html', {'error': str(e)})

@login_required
def disconnect_calendar(request):
    """Clears the stored Google OAuth token"""
    request.user.google_calendar_token = None
    request.user.save()
    return redirect('dashboard')

@login_required
def oauth2callback(request):
    """Handles the OAuth2 callback"""
    state = request.session.get('state')
    if not state:
        return redirect('dashboard')
        
    try:
        flow = get_google_auth_flow(request)
        flow.state = state  # Restore session state to prevent mismatch error
        
        # Google requires the PKCE code_verifier created in the initial step
        code_verifier = request.session.get('code_verifier')
        
        if code_verifier:
            flow.fetch_token(authorization_response=request.build_absolute_uri(), code_verifier=code_verifier)
        else:
            # Fallback if somehow using an older flow that didn't set PKCE
            flow.fetch_token(authorization_response=request.build_absolute_uri())
        
        credentials = flow.credentials
        token_data = json.loads(credentials.to_json())
        has_refresh = 'refresh_token' in token_data
        print(f"DEBUG: New token for {request.user.email}. Refresh token present: {has_refresh}")
        
        request.user.google_calendar_token = token_data
        request.user.save()
        
        return redirect('dashboard')
    except Exception as e:
        return render(request, 'integrations/oauth_error.html', {'error': str(e)})
