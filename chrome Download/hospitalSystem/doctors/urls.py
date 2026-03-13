from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('onboarding/', views.doctor_onboarding, name='doctor_onboarding'),
    path('create-slot/', views.create_slot, name='create_slot'),
]
