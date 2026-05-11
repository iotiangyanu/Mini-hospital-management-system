from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from .models import Availability
from datetime import datetime, timedelta, date
from booking.models import Booking, RejectedBooking
from utils.email_service import send_email
from account.models import User

@login_required
def doctor_dashboard(request):
    # Check if user is doctor
    if request.user.role != 'doctor':
        return redirect('home')

    slots = Availability.objects.filter(doctor=request.user).order_by('date', 'start_time')

    # Only show active bookings (not cancelled)
    bookings = Booking.objects.filter(slot__doctor=request.user).exclude(status='canceled')

    # Group slots by date - only show available slots (not booked)
    slots_by_date = {}
    for slot in slots:
        if not slot.is_booked:  # Only show available slots
            date_key = str(slot.date)
            if date_key not in slots_by_date:
                slots_by_date[date_key] = []
            slots_by_date[date_key].append(slot)

    context = {
        "slots_by_date": slots_by_date,
        "bookings": bookings,
        "doctor_experience": request.user.experience
    }

    return render(request, "doctor_dashboard.html", context)

@login_required
def create_slot(request):
    # Check if user is doctor
    if request.user.role != 'doctor':
        return redirect('home')

    if request.method == "POST":

        date_str = request.POST['date']
        start = request.POST['start']
        end = request.POST['end']
        duration = request.POST.get('duration')

        # Convert date string to date object and validate it's not in the past
        slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if slot_date < date.today():
            return render(request, "create_slot.html", {
                "error": "Cannot create slots for past dates. Please select a future date."
            })

        # Convert times to time objects for proper comparison
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()

        # Validate that start < end
        if start_time >= end_time:
            return render(request, "create_slot.html", {
                "error": "Start time must be before end time."
            })

        # SINGLE SLOT
        if duration == "":

            # Prevent overlap with existing slots
            overlap = Availability.objects.filter(
                doctor=request.user,
                date=date_str,
                start_time__lt=end_time,
                end_time__gt=start_time
            )

            if overlap.exists():
                return render(request, "create_slot.html", {
                    "error": "Cannot create this slot - it overlaps with an existing slot at this time."
                })

            Availability.objects.create(
                doctor=request.user,
                date=date_str,
                start_time=start_time,
                end_time=end_time
            )

        # MULTIPLE SLOTS
        else:

            duration = int(duration)

            # First, check if ANY overlap exists in the entire time range
            overlap = Availability.objects.filter(
                doctor=request.user,
                date=date_str,
                start_time__lt=end_time,
                end_time__gt=start_time
            )

            if overlap.exists():
                return render(request, "create_slot.html", {
                    "error": "Cannot create these slots - the time range overlaps with an existing slot. Please choose a different time."
                })

            # Create a datetime for easier time arithmetic
            start_dt = datetime.combine(slot_date, start_time)
            end_dt = datetime.combine(slot_date, end_time)

            # If no overlap, create all slots
            current = start_dt

            while current < end_dt:

                next_time = current + timedelta(minutes=duration)

                if next_time > end_dt:
                    break

                slot_start = current.time()
                slot_end = next_time.time()

                Availability.objects.create(
                    doctor=request.user,
                    date=date_str,
                    start_time=slot_start,
                    end_time=slot_end
                )

                current = next_time

        return redirect("doctor_dashboard")
    
    return render(request, "create_slot.html")

    return render(request, "create_slot.html")

@login_required
def delete_slot(request, slot_id):
    # Check if user is doctor
    if request.user.role != 'doctor':
        return redirect('home')

    slot = get_object_or_404(Availability, id=slot_id, doctor=request.user)

    # If slot is booked, cancel the booking first
    if slot.is_booked:
        booking = Booking.objects.filter(slot=slot).first()
        if booking:
            # Send cancellation emails
            send_email(
                booking.patient.email,
                "Appointment Cancelled by Doctor",
                f"Hello {booking.patient.full_name},\n\n"
                f"We regret to inform you that your appointment with Dr. {slot.doctor.full_name} "
                f"scheduled for {slot.date.strftime('%d %B %Y')} at {slot.start_time.strftime('%I:%M %p')} "
                f"has been cancelled by the doctor due to unavailability.\n\n"
                f"Please feel free to book another available slot.\n\n"
                f"We apologize for any inconvenience caused.\n\n"
                f"Best Regards,\nMini Hospital Management System"
            )

            send_email(
                slot.doctor.email,
                "Slot Cancelled - Appointment Cancelled",
                f"Dear Dr. {slot.doctor.full_name},\n\n"
                f"You have cancelled the slot scheduled for {slot.date.strftime('%d %B %Y')} "
                f"at {slot.start_time.strftime('%I:%M %p')}.\n\n"
                f"The associated appointment with patient {booking.patient.full_name} "
                f"has been automatically cancelled.\n\n"
                f"Best Regards,\nMini Hospital Management System"
            )

            # Delete the booking
            booking.delete()

    # Delete the slot from the system
    slot.delete()

    return redirect("doctor_dashboard")

def edit_slot(request, slot_id):

    slot = get_object_or_404(Availability, id=slot_id, doctor=request.user)

    if request.method == "POST":

        new_date = request.POST['date']
        new_start = request.POST['start']
        new_end = request.POST['end']

        # Validate date is not in the past
        slot_date = datetime.strptime(new_date, "%Y-%m-%d").date()
        if slot_date < date.today():
            return render(request, "edit_slot.html", {
                "slot": slot,
                "error": "Cannot edit slots to past dates. Please select a future date."
            })

        # Check for overlapping slots (exclude current slot)
        overlap = Availability.objects.filter(
            doctor=request.user,
            date=new_date,
            start_time__lt=new_end,
            end_time__gt=new_start
        ).exclude(id=slot_id)  # Exclude the current slot from overlap check

        if overlap.exists():
            return render(request, "edit_slot.html", {
                "slot": slot,
                "error": "Cannot update slot - overlaps with another existing slot at this time."
            })

        slot.date = new_date
        slot.start_time = new_start
        slot.end_time = new_end
        slot.save()

        return redirect("/doctor/dashboard/")

    return render(request, "edit_slot.html", {"slot": slot})

# @login_required
# def cancel_booking_by_doctor(request, booking_id, slot_id):
#     # Check if user is doctor
#     if request.user.role != 'doctor':
#         return redirect('home')

#     booking = get_object_or_404(Booking, id=booking_id, slot__doctor=request.user)
    
#     booking.is_canceled_by_doctor = True
#     booking.save()

#     # Mark the slot as available
#     booking.slot.is_booked = False
#     booking.slot.save()

#     send_email(
#         request.user.email,
#         "Appointment Confirmed",
#         f"Hello {request.user.full_name}, your appointment with Dr. {slot.doctor.full_name} has been confirmed. \n"
#         f"On {slot.date.strftime('%d %B %Y')} at {slot.start_time.strftime('%I:%M %p')} to {slot.end_time.strftime('%I:%M %p')}"
#     )

#     return redirect("doctor_dashboard")

@login_required
def cancel_booking_by_doctor(request, booking_id):
    # Check if user is doctor
    if request.user.role != 'doctor':
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id, slot__doctor=request.user)
    slot = booking.slot

    # Only allow cancellation if appointment is confirmed
    if booking.status == 'confirmed':
        # Store booking details before deletion for email
        patient_email = booking.patient.email
        patient_name = booking.patient.full_name
        doctor_name = booking.slot.doctor.full_name
        appointment_date = booking.slot.date.strftime('%d %B %Y')
        appointment_time = booking.slot.start_time.strftime('%I:%M %p')

        # Delete the booking completely to free up the slot
        booking.delete()

        # Make slot available again
        slot.is_booked = False
        slot.save()

        # Send email to patient about cancellation
        send_email(
            patient_email,
            "Appointment Cancelled by Doctor",
            f"Hello {patient_name},\n\n"
            f"Your appointment with Dr. {doctor_name} scheduled for "
            f"{appointment_date} at {appointment_time} "
            f"has been cancelled by the doctor.\n\n"
            f"The slot is now available and can be rebooked by you or other patients.\n\n"
            f"Best Regards,\nMini Hospital Management System"
        )

        # Send notification email to doctor
        send_email(
            slot.doctor.email,
            "Appointment Cancelled",
            f"Dear Dr. {doctor_name},\n\n"
            f"You have successfully cancelled the appointment with patient {patient_name}.\n\n"
            f"Appointment Details:\n"
            f"Date: {appointment_date}\n"
            f"Time: {appointment_time}\n\n"
            f"The slot is now available for other patients to book.\n\n"
            f"Best Regards,\nMini Hospital Management System"
        )

    return redirect("doctor_dashboard")


@login_required
def accept_appointment(request, booking_id):
    # Check if user is doctor
    if request.user.role != 'doctor':
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id, slot__doctor=request.user)
    slot = booking.slot

    # Update booking status
    booking.status = 'confirmed'
    booking.save()

    # Send email to patient
    send_email(
        booking.patient.email,
        "Appointment Confirmed",
        f"Hello {booking.patient.full_name},\n\n"
        f"Great news! Your appointment request with Dr. {slot.doctor.full_name} has been confirmed.\n\n"
        f"Appointment Details:\n"
        f"Date: {slot.date.strftime('%d %B %Y')}\n"
        f"Time: {slot.start_time.strftime('%I:%M %p')} to {slot.end_time.strftime('%I:%M %p')}\n"
        f"Doctor: Dr. {slot.doctor.full_name}\n"
        f"Location: Hospital Clinic\n\n"
        f"Please arrive 15 minutes before your appointment time.\n"
        f"If you need to reschedule or cancel, please contact us.\n\n"
        f"Best Regards,\nMini Hospital Management System"
    )

    # Send confirmation email to doctor
    send_email(
        slot.doctor.email,
        "Appointment Confirmed",
        f"Dear Dr. {slot.doctor.full_name},\n\n"
        f"You have confirmed the appointment with patient {booking.patient.full_name}.\n\n"
        f"Appointment Details:\n"
        f"Date: {slot.date.strftime('%d %B %Y')}\n"
        f"Time: {slot.start_time.strftime('%I:%M %p')} to {slot.end_time.strftime('%I:%M %p')}\n"
        f"Patient: {booking.patient.full_name} ({booking.patient.email})\n\n"
        f"Best Regards,\nMini Hospital Management System"
    )

    return redirect("doctor_dashboard")


@login_required
def reject_appointment(request, booking_id):
    # Check if user is doctor
    if request.user.role != 'doctor':
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id, slot__doctor=request.user)
    slot = booking.slot

    # Store booking details before deletion for email
    patient_email = booking.patient.email
    patient_name = booking.patient.full_name
    doctor_name = slot.doctor.full_name
    appointment_date = slot.date.strftime('%d %B %Y')
    appointment_time = slot.start_time.strftime('%I:%M %p')

    # Add patient to rejected bookings for this slot
    RejectedBooking.objects.get_or_create(
        patient=booking.patient,
        slot=slot
    )

    # Delete the booking completely to free up the slot
    booking.delete()

    # Make slot available again
    slot.is_booked = False
    slot.save()

    # Send email to patient
    send_email(
        patient_email,
        "Appointment Request Rejected",
        f"Hello {patient_name},\n\n"
        f"We regret to inform you that your appointment request with Dr. {doctor_name} "
        f"for {appointment_date} at {appointment_time} "
        f"has been rejected by the doctor.\n\n"
        f"This could be due to scheduling conflicts or other reasons. "
        f"Please feel free to book another available slot.\n\n"
        f"We apologize for any inconvenience caused.\n\n"
        f"Best Regards,\nMini Hospital Management System"
    )

    # Send notification email to doctor
    send_email(
        slot.doctor.email,
        "Appointment Rejected",
        f"Dear Dr. {doctor_name},\n\n"
        f"You have rejected the appointment request from patient {patient_name}.\n\n"
        f"Appointment Details:\n"
        f"Date: {appointment_date}\n"
        f"Time: {appointment_time}\n"
        f"Patient: {patient_name} ({patient_email})\n\n"
        f"The slot is now available for other patients to book.\n\n"
        f"Best Regards,\nMini Hospital Management System"
    )

    return redirect("doctor_dashboard")