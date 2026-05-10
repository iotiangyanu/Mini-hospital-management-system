from django.shortcuts import render, redirect, get_object_or_404
from doctors.models import Availability
from .models import Booking, RejectedBooking
from account.models import User
from datetime import datetime, date
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

    # Only show active bookings (not cancelled)
    bookings = Booking.objects.filter(patient=request.user).exclude(status='canceled')
    for doctor in doctors:
        doctor.year_difference = datetime.now().year - doctor.practicing_year_from

    context = {
        "doctors": doctors,
        "bookings": bookings,
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
    ).exclude(
        # Exclude slots that this patient has rejected
        id__in=RejectedBooking.objects.filter(patient=request.user).values('slot_id')
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

    # Check if slot is already booked
    if slot.is_booked:
        return render(request, "doctor_slots.html", {
            "error": "This slot is no longer available. Please choose another slot.",
            "doctor": slot.doctor
        })

    # Check if user already has a booking for this slot
    if Booking.objects.filter(patient=request.user, slot=slot).exists():
        return render(request, "doctor_slots.html", {
            "error": "You have already booked this slot.",
            "doctor": slot.doctor
        })

    try:
        booking = Booking.objects.create(
            patient=request.user,
            slot=slot,
            status='pending'
        )

        slot.is_booked = True
        slot.save()
    except Exception as e:
        # Handle any database constraint violations
        return render(request, "doctor_slots.html", {
            "error": "This slot is no longer available. Please choose another slot.",
            "doctor": slot.doctor
        })

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

    # Email to Patient - Appointment Request Submitted
    send_email(
        request.user.email,
        "Appointment Request Submitted",
        f"Hello {request.user.full_name},\n\n"
        f"Your appointment request with Dr. {slot.doctor.full_name} has been submitted.\n"
        f"Date: {slot.date.strftime('%d %B %Y')}\n"
        f"Time: {slot.start_time.strftime('%I:%M %p')} to {slot.end_time.strftime('%I:%M %p')}\n\n"
        f"Status: Pending (waiting for doctor's approval)\n\n"
        f"You will receive an email once the doctor reviews your request.\n\n"
        f"Best Regards,\nMini Hospital Management System"
    )

    # Email to Doctor - New Appointment Request
    send_email(
        slot.doctor.email,
        "New Appointment Request",
        f"Dear Dr. {slot.doctor.full_name},\n\n"
        f"You have received a new appointment request from patient {request.user.full_name}.\n\n"
        f"Patient Details:\n"
        f"Name: {request.user.full_name}\n"
        f"Email: {request.user.email}\n"
        f"Mobile: {request.user.mobile_number}\n"
        f"Gender: {request.user.gender}\n\n"
        f"Appointment Details:\n"
        f"Date: {slot.date.strftime('%d %B %Y')}\n"
        f"Time: {slot.start_time.strftime('%I:%M %p')} to {slot.end_time.strftime('%I:%M %p')}\n\n"
        f"Please log in to your dashboard to accept or reject this appointment.\n\n"
        f"Best Regards,\nMini Hospital Management System"
    )

    return redirect("/patient/dashboard/")
@login_required
def cancel_booking(request, booking_id):
    # Check if user is patient
    if request.user.role != 'patient':
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id, patient=request.user)

    # Only allow cancellation if appointment is confirmed
    if booking.status == 'confirmed':
        # Store booking details before deletion for email
        doctor_email = booking.slot.doctor.email
        doctor_name = booking.slot.doctor.full_name
        patient_name = booking.patient.full_name
        patient_email = booking.patient.email
        appointment_date = booking.slot.date.strftime('%d %B %Y')
        appointment_time = booking.slot.start_time.strftime('%I:%M %p')

        # Delete the booking completely to free up the slot
        booking.delete()

        # Make slot available again
        booking.slot.is_booked = False
        booking.slot.save()

        # Send email to doctor about cancellation
        send_email(
            doctor_email,
            "Appointment Cancelled by Patient",
            f"Dear Dr. {doctor_name},\n\n"
            f"Patient {patient_name} has cancelled their confirmed appointment.\n\n"
            f"Appointment Details:\n"
            f"Date: {appointment_date}\n"
            f"Time: {appointment_time}\n\n"
            f"The slot is now available for other patients to book.\n\n"
            f"Best Regards,\nMini Hospital Management System"
        )

        # Send confirmation email to patient
        send_email(
            patient_email,
            "Appointment Cancelled",
            f"Hello {patient_name},\n\n"
            f"Your appointment with Dr. {doctor_name} scheduled for "
            f"{appointment_date} at {appointment_time} "
            f"has been successfully cancelled.\n\n"
            f"The slot is now available and can be rebooked by you or other patients.\n\n"
            f"Best Regards,\nMini Hospital Management System"
        )

    return redirect("patient_dashboard")