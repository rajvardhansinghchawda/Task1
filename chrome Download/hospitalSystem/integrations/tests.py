import json
import datetime
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from unittest.mock import patch, MagicMock

from users.models import User
from doctors.models import Doctor, AvailabilitySlot
from appointments.models import Appointment
from integrations.views import google_calendar_init, oauth2callback
from integrations.google_calendar import create_calendar_event, _get_valid_credentials

class GoogleCalendarIntegrationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create users
        self.patient = User.objects.create_user(
            email='patient@test.com',
            password='testpassword',
            name='Test Patient',
            role='PATIENT'
        )
        
        self.doc_user = User.objects.create_user(
            email='doctor@test.com',
            password='testpassword',
            name='Test Doctor',
            role='DOCTOR'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doc_user,
            specialization='Cardiology',
            hospital_name='Test Hospital'
        )
        
        # Create slot and appointment
        self.slot = AvailabilitySlot.objects.create(
            doctor=self.doctor,
            date=datetime.date(2026, 3, 20),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(10, 30),
            is_booked=True
        )
        
        self.appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            slot=self.slot,
            status='CONFIRMED'
        )
        
        # Valid Mock token mapping
        self.valid_token = {
            "token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "mock-id",
            "client_secret": "mock-secret",
            "scopes": ["https://www.googleapis.com/auth/calendar.events"]
        }

    @patch('integrations.google_calendar.build')
    @patch('integrations.google_calendar._get_valid_credentials')
    def test_create_event_for_doctor(self, mock_get_creds, mock_build):
        """Test Calendar event structure for the Doctor's perspective"""
        # Mock valid credentials
        mock_creds = MagicMock()
        mock_get_creds.return_value = mock_creds
        
        # Mock Google Calendar API service
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_build.return_value = mock_service
        mock_service.events.return_value = mock_events
        mock_events.insert.return_value = mock_insert
        
        # Call the function for doctor
        self.doc_user.google_calendar_token = self.valid_token
        self.doc_user.save()
        result = create_calendar_event(self.doc_user, self.appointment, is_doctor=True)
        
        self.assertTrue(result)
        mock_insert.execute.assert_called_once()
        
        # Assert the event payload structure is correct
        called_kwargs = mock_events.insert.call_args[1]
        self.assertEqual(called_kwargs['calendarId'], 'primary')
        
        event_body = called_kwargs['body']
        self.assertEqual(event_body['summary'], 'Appointment with Test Patient')
        self.assertTrue('Test Doctor' in event_body['description'])
        self.assertTrue('Test Patient' in event_body['description'])
        self.assertEqual(event_body['location'], 'Test Hospital')
        
    @patch('integrations.google_calendar.build')
    @patch('integrations.google_calendar._get_valid_credentials')
    def test_create_event_for_patient(self, mock_get_creds, mock_build):
        """Test Calendar event structure for the Patient's perspective"""
        mock_creds = MagicMock()
        mock_get_creds.return_value = mock_creds
        
        mock_service = MagicMock()
        mock_events = MagicMock()
        mock_insert = MagicMock()
        mock_build.return_value = mock_service
        mock_service.events.return_value = mock_events
        mock_events.insert.return_value = mock_insert
        
        # Call the function for patient
        self.patient.google_calendar_token = self.valid_token
        self.patient.save()
        result = create_calendar_event(self.patient, self.appointment, is_doctor=False)
        
        self.assertTrue(result)
        
        # Assert payload
        event_body = mock_events.insert.call_args[1]['body']
        self.assertEqual(event_body['summary'], 'Appointment with Dr. Test Doctor')
        self.assertTrue('Test Doctor' in event_body['description'])
        self.assertTrue('Test Patient' in event_body['description'])
        self.assertEqual(event_body['location'], 'Test Hospital')

    @patch('integrations.google_calendar.Credentials.from_authorized_user_info')
    def test_token_refresh(self, mock_from_user_info):
        """Test that an expired token tries to refresh and persists to DB"""
        self.patient.google_calendar_token = self.valid_token
        self.patient.save()
        
        mock_creds = MagicMock()
        mock_creds.expired = True
        mock_creds.refresh_token = "mock-refresh-token"
        mock_creds.valid = True
        mock_creds.to_json.return_value = '{"token": "new-mock-token", "refresh_token": "mock-refresh-token", "token_uri": "https://oauth2.googleapis.com/token", "client_id": "mock-id", "client_secret": "mock-secret", "scopes": []}'
        
        mock_from_user_info.return_value = mock_creds
        
        creds = _get_valid_credentials(self.patient)
        
        # It should call refresh()
        mock_creds.refresh.assert_called_once()
        self.assertIsNotNone(creds)
        
        # It should save the new token back to DB
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.google_calendar_token["token"], "new-mock-token")
