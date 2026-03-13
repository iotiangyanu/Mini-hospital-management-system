from django.shortcuts import render, redirect, get_object_or_404
from doctors.models import Availability
from .models import Booking
from account.models import User
from datetime import date
from django.contrib.auth.decorators import login_required
from utils.email_service import send_email
from utils.google_calendar import create_event
import logging

logger = logging.getLogger(__name__)


@login_required
def patient_dashboard(request):
    # Check if user is patient
    if request.user.role != 'patient':
        return redirect('home')

    doctors = User.objects.filter(role="doctor")

    bookings = Booking.objects.filter(patient=request.user)

    context = {
        "doctors": doctors,
        "bookings": bookings
    }

    return render(request, "patient_dashboard.html", context)


@login_required
def doctor_slots(request, doctor_id):
    # Check if user is patient
    if request.user.role != 'patient':
        return redirect('home')

    slots = Availability.objects.filter(
        doctor_id=doctor_id,
        is_booked=False,
        date__gte=date.today()
    ).order_by('date', 'start_time')

    # Group slots by date
    slots_by_date = {}
    for slot in slots:
        date_key = str(slot.date)
        if date_key not in slots_by_date:
            slots_by_date[date_key] = []
        slots_by_date[date_key].append(slot)

    doctor = User.objects.get(id=doctor_id)
    context = {
        "slots_by_date": slots_by_date,
        "doctor": doctor
    }

    return render(request, "doctor_slots.html", context)


@login_required
def book_slot(request, slot_id):

    slot = Availability.objects.get(id=slot_id)

    booking = Booking.objects.create(
        patient=request.user,
        slot=slot
    )

    slot.is_booked = True
    slot.save()

    # Google Calendar Event
    try:

        start_time = f"{slot.date}T{slot.start_time}"
        end_time = f"{slot.date}T{slot.end_time}"

        create_event(
            doctor_email=slot.doctor.email,
            patient_email=request.user.email,
            start_time=start_time,
            end_time=end_time,
            doctor_name=slot.doctor.full_name,
            patient_name=request.user.full_name
        )

    except Exception as e:
        print("Calendar error:", e)

    # Email to Patient
    send_email(
        request.user.email,
        "Appointment Confirmed",
        f"Hello {request.user.full_name}, your appointment with Dr. {slot.doctor.full_name} has been confirmed."
    )

    # Email to Doctor
    send_email(
        slot.doctor.email,
        "New Appointment Booked",
        f"Patient {request.user.full_name} has booked an appointment."
    )

    return redirect("/patient/dashboard/")
@login_required
def cancel_booking(request, booking_id):
    # Check if user is patient
    if request.user.role != 'patient':
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id, patient=request.user)

    booking.slot.is_booked = False
    booking.slot.save()

    booking.delete()

    return redirect("patient_dashboard")