from django.contrib import admin
from .models import Doctor, AvailabilitySlot

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'hospital_name', 'experience')
    search_fields = ('user__name', 'specialization', 'hospital_name')
    list_filter = ('specialization',)

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('is_booked', 'date')
    search_fields = ('doctor__user__name',)
