import json
import pytest
from unittest.mock import patch, MagicMock
from handler import send_email
import os

@pytest.fixture
def mock_env():
    # Setup valid environment variables
    with patch.dict(os.environ, {
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': '587',
        'SMTP_USER': 'test@example.com',
        'SMTP_PASS': 'secret'
    }):
        yield

def test_missing_smtp_config():
    with patch.dict(os.environ, {'SMTP_SERVER': '', 'SMTP_USER': '', 'SMTP_PASS': ''}):
        event = {'body': json.dumps({'type': 'SIGNUP_WELCOME', 'email': 'user@test.com'})}
        response = send_email(event, None)
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'SMTP is not configured' in body['message']

@patch('handler.smtplib.SMTP')
def test_valid_signup_welcome(mock_smtp, mock_env):
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
    
    event = {
        'body': json.dumps({
            'type': 'SIGNUP_WELCOME',
            'email': 'user@test.com',
            'data': {'name': 'John Doe'}
        })
    }
    response = send_email(event, None)
    
    assert response['statusCode'] == 200
    mock_smtp_instance.send_message.assert_called_once()
    msg = mock_smtp_instance.send_message.call_args[0][0]
    assert msg['Subject'] == 'Welcome to Hospital HMS'
    assert msg['To'] == 'user@test.com'

@patch('handler.smtplib.SMTP')
def test_valid_booking_confirmation(mock_smtp, mock_env):
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
    
    event = {
        'body': json.dumps({
            'type': 'BOOKING_CONFIRMATION',
            'email': 'patient@test.com',
            'data': {
                'doctor': 'Dr. Smith',
                'patient': 'Jane Doe',
                'date': '2026-03-20',
                'time': '10:00:00 - 10:30:00'
            }
        })
    }
    response = send_email(event, None)
    
    assert response['statusCode'] == 200
    mock_smtp_instance.send_message.assert_called_once()
    msg = mock_smtp_instance.send_message.call_args[0][0]
    assert msg['Subject'] == 'Appointment Confirmed'

@patch('handler.smtplib.SMTP')
def test_valid_doctor_notification(mock_smtp, mock_env):
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
    
    event = {
        'body': json.dumps({
            'type': 'BOOKING_NOTIFICATION_DOCTOR',
            'email': 'doctor@test.com',
            'data': {
                'doctor': 'Dr. Smith',
                'patient': 'Jane Doe',
                'date': '2026-03-20',
                'time': '10:00:00 - 10:30:00'
            }
        })
    }
    response = send_email(event, None)
    
    assert response['statusCode'] == 200
    mock_smtp_instance.send_message.assert_called_once()
    msg = mock_smtp_instance.send_message.call_args[0][0]
    assert msg['Subject'] == 'New Appointment Booked'
    assert 'Jane Doe' in str(msg.get_content())

def test_invalid_type(mock_env):
    event = {
        'body': json.dumps({
            'type': 'INVALID_TYPE',
            'email': 'user@test.com'
        })
    }
    response = send_email(event, None)
    assert response['statusCode'] == 400
