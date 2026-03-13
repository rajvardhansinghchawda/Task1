from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from doctors.models import Doctor, AvailabilitySlot
from appointments.models import Appointment
from django.db import transaction
from django.utils import timezone
from integrations.google_calendar import create_calendar_event
from notifications.email_service import send_booking_confirmation, send_booking_notification_to_doctor

@login_required
def patient_dashboard(request):
    if request.user.role != 'PATIENT':
        return redirect('dashboard')
        
    appointments = Appointment.objects.filter(patient=request.user).order_by('slot__date', 'slot__start_time')
    return render(request, 'appointments/patient_dashboard.html', {'appointments': appointments})

@login_required
def doctor_list(request):
    if request.user.role != 'PATIENT':
        return redirect('dashboard')
        
    doctors = Doctor.objects.all()
    return render(request, 'appointments/doctor_list.html', {'doctors': doctors})

@login_required
def doctor_slots(request, doctor_id):
    if request.user.role != 'PATIENT':
        return redirect('dashboard')
        
    doctor = get_object_or_404(Doctor, id=doctor_id)
    # Only show future slots that are not booked
    today = timezone.localdate()
    slots = AvailabilitySlot.objects.filter(doctor=doctor, is_booked=False, date__gte=today).order_by('date', 'start_time')
    
    return render(request, 'appointments/doctor_slots.html', {'doctor': doctor, 'slots': slots})

@login_required
def book_appointment(request, slot_id):
    if request.user.role != 'PATIENT':
        return redirect('dashboard')
        
    if request.method == 'POST':
        with transaction.atomic():
            # Lock the slot row to prevent race conditions during booking
            slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
            
            if slot.is_booked:
                # In a real app, add a messages framework alert here
                return redirect('doctor_slots', doctor_id=slot.doctor.id)
                
            # Create an appointment
            appointment = Appointment.objects.create(
                doctor=slot.doctor,
                patient=request.user,
                slot=slot,
                status='CONFIRMED'
            )
            
            # Mark the slot as booked
            slot.is_booked = True
            slot.save()
            
            # Google Calendar Integration
            create_calendar_event(slot.doctor.user, appointment, is_doctor=True)
            create_calendar_event(request.user, appointment, is_doctor=False)
            
            # Trigger Email Notifications
            send_booking_confirmation(request.user.email, appointment)
            send_booking_notification_to_doctor(slot.doctor.user.email, appointment)
            
            return redirect('patient_dashboard')
            
    return redirect('doctor_list')
