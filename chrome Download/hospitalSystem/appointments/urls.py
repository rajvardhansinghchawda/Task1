from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/<int:doctor_id>/slots/', views.doctor_slots, name='doctor_slots'),
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
]
