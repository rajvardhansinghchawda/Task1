from django.urls import path
from . import views

urlpatterns = [
    path('google/login/', views.google_calendar_init, name='google_calendar_init'),
    path('google/disconnect/', views.disconnect_calendar, name='google_calendar_disconnect'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
]
