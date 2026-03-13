from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.email_signup, name='email_signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('select-role/', views.select_role, name='select_role'),
    path('onboarding/patient/', views.patient_onboarding, name='patient_onboarding'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard_redirect, name='dashboard'),
]
