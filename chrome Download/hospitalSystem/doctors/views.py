from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Doctor, AvailabilitySlot
from .forms import SlotGeneratorForm, DoctorProfileForm
from appointments.models import Appointment
from datetime import datetime, timedelta, date

@login_required
def doctor_dashboard(request):
    if request.user.role != 'DOCTOR':
        return redirect('dashboard')
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('doctor_onboarding')
    
    doctor = request.user.doctor_profile
    slots = AvailabilitySlot.objects.filter(doctor=doctor).order_by('date', 'start_time')
    appointments = Appointment.objects.filter(doctor=doctor).order_by('slot__date', 'slot__start_time')
    
    context = {
        'doctor': doctor,
        'slots': slots,
        'appointments': appointments,
    }
    return render(request, 'doctors/dashboard.html', context)

@login_required
def create_slot(request):
    if request.user.role != 'DOCTOR':
        return redirect('dashboard')
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('doctor_onboarding')
        
    doctor = request.user.doctor_profile
    if request.method == 'POST':
        form = SlotGeneratorForm(request.POST)
        if form.is_valid():
            slot_date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            duration_minutes = int(form.cleaned_data['slot_duration_minutes'])
            
            # Combine into full datetime objects for easy math
            current_datetime = datetime.combine(slot_date, start_time)
            end_datetime = datetime.combine(slot_date, end_time)
            delta = timedelta(minutes=duration_minutes)
            
            slots_to_create = []
            duplicate_count = 0
            
            # Loop and generate slots until we reach the end time
            while current_datetime + delta <= end_datetime:
                # Add slot end boundary
                slot_end = current_datetime + delta
                
                # Check for existing duplicate slot
                if not AvailabilitySlot.objects.filter(
                    doctor=doctor,
                    date=slot_date,
                    start_time=current_datetime.time(),
                    end_time=slot_end.time()
                ).exists():
                    # Instanciate but don't save to DB individually
                    new_slot = AvailabilitySlot(
                        doctor=doctor,
                        date=slot_date,
                        start_time=current_datetime.time(),
                        end_time=slot_end.time(),
                        is_booked=False
                    )
                    slots_to_create.append(new_slot)
                else:
                    duplicate_count += 1
                
                # Move to the next interval
                current_datetime = slot_end
                
            # Efficiently write all generated slots to database
            if slots_to_create:
                AvailabilitySlot.objects.bulk_create(slots_to_create)
                messages.success(request, f'Successfully generated {len(slots_to_create)} slots.')
                
            if duplicate_count > 0:
                messages.warning(request, f'Skipped {duplicate_count} slots that already existed.')
                
            if len(slots_to_create) == 0 and duplicate_count == 0:
                messages.error(request, 'No slots could be generated. Check your time intervals.')
            
            return redirect('doctor_dashboard')
    else:
        initial_data = {'date': date.today()}
        if doctor.available_from:
            initial_data['start_time'] = doctor.available_from
        if doctor.available_to:
            initial_data['end_time'] = doctor.available_to
        if doctor.default_slot_duration:
            initial_data['slot_duration_minutes'] = doctor.default_slot_duration
            
        form = SlotGeneratorForm(initial=initial_data)
        
    return render(request, 'doctors/create_slot.html', {'form': form})

@login_required
def view_profile(request):
    if request.user.role != 'DOCTOR':
        return redirect('dashboard')
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('doctor_onboarding')
        
    doctor = get_object_or_404(Doctor, user=request.user)
    return render(request, 'doctors/view_profile.html', {'doctor': doctor})
    
@login_required
def edit_profile(request):
    if request.user.role != 'DOCTOR':
        return redirect('dashboard')
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('doctor_onboarding')
        
    doctor = get_object_or_404(Doctor, user=request.user)
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('view_profile')
    else:
        form = DoctorProfileForm(instance=doctor)
        
    return render(request, 'doctors/edit_profile.html', {'form': form})

@login_required
def doctor_onboarding(request):
    if request.user.role != 'DOCTOR':
        return redirect('dashboard')
        
    if hasattr(request.user, 'doctor_profile'):
        return redirect('doctor_dashboard')
        
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES)
        if form.is_valid():
            doctor_profile = form.save(commit=False)
            doctor_profile.user = request.user
            doctor_profile.save()
            messages.success(request, 'Profile created successfully! Welcome to the dashboard.')
            return redirect('doctor_dashboard')
    else:
        form = DoctorProfileForm()
        
    return render(request, 'doctors/onboarding.html', {'form': form})
