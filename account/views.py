from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import User, TemporaryRegistration
from utils.email_service import send_email
import random
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta


def home(request):
    return render(request, "home.html")


def user_login(request, role):

    # If user already authenticated
    if request.user.is_authenticated:
        if request.user.role == "doctor":
            return redirect("/doctor/dashboard/")
        else:
            return redirect("/patient/dashboard/")


    if request.method == "POST":

        identifier = request.POST.get('identifier')
        password = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=identifier)
            username = user_obj.username
        except User.DoesNotExist:
            username = identifier

        user = authenticate(request,username=username, password=password)

        if user:

            # Prevent wrong role login
            if user.role != role:

                return render(request, "login.html", {
                    "role": role,
                    "error": "Invalid credentials"
                })

            login(request, user)

            if role == "doctor":
                return redirect("/doctor/dashboard/")
            else:
                return redirect("/patient/dashboard/")

        else:
            return render(request, "login.html", {
                "role": role,
                "error": "Invalid username/email or password"
            })

    return render(request, "login.html", {"role": role})



def register(request, role):

    if request.user.is_authenticated:
        if request.user.role == "doctor":
            return redirect("/doctor/dashboard/")
        return redirect("/patient/dashboard/")

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        full_name = request.POST.get("full_name")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        mobile = request.POST.get("mobile")

        qualification = request.POST.get("qualification")
        specialization = request.POST.get("specialization")
        experience = request.POST.get("experience")
        license_number = request.POST.get("license_number")

        blood_group = request.POST.get("blood_group")
        illness = request.POST.get("illness")

        # Validate password confirmation
        if password != confirm_password:
            return render(request, "register.html", {
                "role": role,
                "error": "Passwords do not match. Please try again."
            })

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "role": role,
                "error": "Username already taken. Please choose a different username."
            })

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {
                "role": role,
                "error": "Email already registered. Please use a different email or try logging in."
            })

        # Check if temporary registration exists
        if TemporaryRegistration.objects.filter(email=email).exists():
            temp_reg = TemporaryRegistration.objects.get(email=email)
            # If OTP is expired, allow new registration
            if timezone.now() > temp_reg.otp_created_at + timedelta(seconds=180):
                temp_reg.delete()
            else:
                return render(request, "register.html", {
                    "role": role,
                    "error": "OTP verification pending for this email. Please check your email and verify."
                })

        # Generate 5-digit OTP
        otp = str(random.randint(10000, 99999))

        # Hash password
        hashed_password = make_password(password)

        # Save temporary registration
        temp_reg = TemporaryRegistration.objects.create(
            email=email,
            username=username,
            password=hashed_password,
            otp=otp,
            role=role,
            full_name=full_name,
            gender=gender,
            date_of_birth=dob,
            mobile_number=mobile,
            qualification=qualification,
            specialization=specialization,
            experience_years=experience,
            license_number=license_number,
            blood_group=blood_group,
            illness_description=illness
        )

        # Send OTP email
        otp_message = f"""Your OTP for Mini Hospital Management System registration is: {otp}

                        This OTP is valid for 180 seconds.

                        If you did not request this, please ignore this email.

                        Best Regards,
                        Mini Hospital Management System Team"""

        try:
            result = send_email(
                email,
                "OTP for HMS Registration",
                otp_message
            )
            if not result:
                temp_reg.delete()
                return render(request, "register.html", {
                    "role": role,
                    "error": "Failed to send OTP email. Please try again."
                })
        except Exception as e:
            temp_reg.delete()
            return render(request, "register.html", {
                "role": role,
                "error": e
            })

        # Redirect to OTP verification page
        return redirect(reverse('verify_otp', kwargs={'role': role, 'email': email}))

    return render(request, "register.html", {"role": role})


def verify_otp(request, role, email):
    if request.user.is_authenticated:
        if request.user.role == "doctor":
            return redirect("/doctor/dashboard/")
        return redirect("/patient/dashboard/")

    try:
        temp_reg = TemporaryRegistration.objects.get(email=email)
    except TemporaryRegistration.DoesNotExist:
        return render(request, "otp_verify.html", {
            "role": role,
            "email": email,
            "error": "No pending registration found for this email."
        })

    otp_age = timezone.now() - temp_reg.otp_created_at
    remaining_seconds = max(0, 180 - int(otp_age.total_seconds()))

    if request.method == "POST":
        otp_entered = request.POST.get("otp", "").strip()

        # Check if OTP is expired
        if remaining_seconds == 0:
            return render(request, "otp_verify.html", {
                "role": role,
                "email": email,
                "error": "OTP has expired. Please request a new one.",
                "remaining_seconds": remaining_seconds
            })

        # Strict OTP validation
        if not otp_entered.isdigit() or len(otp_entered) != 5:
            return render(request, "otp_verify.html", {
                "role": role,
                "email": email,
                "error": "OTP is wrong. Please try again.",
                "remaining_seconds": remaining_seconds
            })

        if otp_entered == temp_reg.otp:
            # Create the user using the already hashed password
            user = User.objects.create(
                username=temp_reg.username,
                email=temp_reg.email,
                role=temp_reg.role,
                full_name=temp_reg.full_name,
                gender=temp_reg.gender,
                date_of_birth=temp_reg.date_of_birth,
                mobile_number=temp_reg.mobile_number,
                qualification=temp_reg.qualification,
                specialization=temp_reg.specialization,
                experience_years=temp_reg.experience_years,
                license_number=temp_reg.license_number,
                blood_group=temp_reg.blood_group,
                illness_description=temp_reg.illness_description,
                password=temp_reg.password,
            )

            # Delete temporary registration
            temp_reg.delete()

            # Send welcome email
            role_title = "Doctor" if role == "doctor" else "Patient"
            welcome_message = f"""Welcome to Mini Hospital Management System (HMS)

                                Dear {user.full_name},

                                We are pleased to inform you that your account has been successfully created as a {role_title}.

                                --- ACCOUNT DETAILS ---
                                Username: {user.username}
                                Email: {user.email}
                                Role: {role_title}

                                --- NEXT STEPS ---
                                {f"Please log in to create your availability slots and start accepting patient appointments." if role == "doctor" else "You can now log in and book appointments with our experienced doctors."}

                                To log in, visit: http://localhost:8000/login/{role}/

                                If you have any questions or need assistance, please contact us.

                                Best Regards,
                                Mini Hospital Management System Team"""

            try:
                send_email(
                    user.email,
                    f"Welcome to HMS - {role_title} Account Created",
                    welcome_message
                )
            except Exception as e:
                print(f"Error sending welcome email: {str(e)}")

            return redirect(reverse('login', kwargs={'role': role}))
        else:
            return render(request, "otp_verify.html", {
                "role": role,
                "email": email,
                "error": "OTP is wrong. Enter correct OTP.",
                "remaining_seconds": remaining_seconds
            })

    return render(request, "otp_verify.html", {
        "role": role,
        "email": email,
        "remaining_seconds": remaining_seconds
    })


def resend_otp(request, role, email):
    try:
        temp_reg = TemporaryRegistration.objects.get(email=email)
    except TemporaryRegistration.DoesNotExist:
        return render(request, "otp_verify.html", {
            "role": role,
            "email": email,
            "error": "No pending registration found for this email."
        })

    # Only allow a new OTP after the current one has expired
    otp_age = timezone.now() - temp_reg.otp_created_at
    if otp_age < timedelta(seconds=180):
        remaining = int((timedelta(seconds=180) - otp_age).total_seconds())
        return render(request, "otp_verify.html", {
            "role": role,
            "email": email,
            "error": f"OTP is still valid. Please wait {remaining} seconds before requesting a new OTP.",
            "remaining_seconds": remaining
        })

    # Generate new OTP after expiry
    otp = str(random.randint(10000, 99999))
    temp_reg.otp = otp
    temp_reg.otp_created_at = timezone.now()
    temp_reg.save()

    # Send new OTP email
    otp_message = f"""Your new OTP for Mini Hospital Management System registration is: {otp}

This OTP is valid for 180 seconds.

If you did not request this, please ignore this email.

Best Regards,
Mini Hospital Management System Team"""

    try:
        result = send_email(
            email,
            "New OTP for HMS Registration",
            otp_message
        )
        if not result:
            return render(request, "otp_verify.html", {
                "role": role,
                "email": email,
                "error": "Failed to send new OTP email. Please try again.",
                "remaining_seconds": 180
            })
    except Exception as e:
        return render(request, "otp_verify.html", {
            "role": role,
            "email": email,
            "error": "Error sending new OTP email. Please try again.",
            "remaining_seconds": 180
        })

    return render(request, "otp_verify.html", {
        "role": role,
        "email": email,
        "success": "New OTP sent to your email.",
        "remaining_seconds": 180
    })


def logout_view(request):
    logout(request)
    return redirect('home')