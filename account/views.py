from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import User
from utils.email_service import send_email


def home(request):
    return render(request, "home.html")


def user_login(request, role):

    # If user already authenticated
    if request.user.is_authenticated:

        # If same role → redirect to dashboard
        if request.user.role == role:

            if role == "doctor":
                return redirect("/doctor/dashboard/")
            else:
                return redirect("/patient/dashboard/")

        # If different role → show login page normally
        else:
            return render(request, "login.html", {"role": role})


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

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
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

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
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

        # Send Welcome Email with proper formatting
        role_title = "Doctor" if role == "doctor" else "Patient"
        welcome_message = f"""Welcome to Mini Hospital Management System (HMS)

Dear {user.full_name},

We are pleased to inform you that your account has been successfully created as a {role_title}.

--- ACCOUNT DETAILS ---
Username: {username}
Email: {user.email}
Role: {role_title}

--- NEXT STEPS ---
{f"Please log in to create your availability slots and start accepting patient appointments." if role == "doctor" else "You can now log in and book appointments with our experienced doctors."}

To log in, visit: http://localhost:8000/login/{role}/

If you have any questions or need assistance, please contact us.

Best Regards,
Mini Hospital Management System Team"""

        try:
            result = send_email(
                user.email,
                f"Welcome to HMS - {role_title} Account Created",
                welcome_message
            )
            if not result:
                print(f"Warning: Could not send welcome email to {user.email}")
        except Exception as e:
            print(f"Error sending welcome email: {str(e)}")

        return redirect(f"/login/{role}/")

    return render(request, "register.html", {"role": role})


def logout_view(request):
    logout(request)
    return redirect('home')