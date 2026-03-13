# Mini Hospital Management System (HMS)

## Overview

The **Mini Hospital Management System (HMS)** is a web-based application developed using the **Django framework**. The purpose of this project is to simplify hospital operations such as **doctor scheduling, patient management, and appointment booking**.

The system provides a structured platform where **patients can book appointments with doctors**, and **doctors can manage their availability and appointments efficiently**. This project reduces manual effort, avoids scheduling conflicts, and improves communication between doctors and patients.

This project is designed as a **mini project for learning and demonstration purposes**, showcasing the implementation of **backend development using Django, database integration, authentication, and scheduling logic**.

---

# Key Features

### 1. User Authentication

The system supports authentication for different types of users.

* Doctor Registration
* Patient Registration
* Secure Login System
* Role-based access for doctors and patients

Each user can create an account and securely access the system using their credentials.

---

### 2. Doctor Dashboard

Doctors have a dedicated dashboard where they can manage their work.

Features available to doctors:

* Create available appointment slots
* Edit or delete appointment slots
* View booked appointments
* Manage patient appointments

This allows doctors to control their availability and schedule efficiently.

---

### 3. Patient Dashboard

Patients can interact with doctors through the patient dashboard.

Patients can:

* View available doctors
* View available appointment slots
* Book appointments with doctors
* Check their booked appointments

This simplifies the appointment booking process.

---

### 4. Appointment Slot Management

Doctors can create specific time slots for appointments.

The system ensures:

* Only available slots can be booked
* One patient can book one slot at a time
* Slots become unavailable once booked

This prevents **double booking or scheduling conflicts**.

---

### 5. Email Notification System

The system includes an **email notification feature**.

When certain actions occur, email notifications are sent automatically.

Examples:

* Doctor registration confirmation
* Patient registration confirmation
* Appointment booking confirmation

This improves communication between users and the system.

---

### 6. Google Calendar Integration

The system also supports **Google Calendar integration**.

When an appointment is booked:

* An event can be created in Google Calendar
* Doctors can track appointments easily

This helps manage schedules more effectively.

---

# Technologies Used

### Backend

* Python
* Django Framework

### Frontend

* HTML
* CSS
* Django Templates

### Database

* PostgreSQL (Primary)
* SQLite (Optional for testing)

### Other Technologies

* Google Calendar API
* SMTP Email Service
* Django ORM

---

# Project Structure

mini_hms/

│

├── account/ → Handles user registration and authentication

├── doctors/ → Doctor management and slot creation

├── booking/ → Appointment booking system

├── utils/ → Email services and Google Calendar integration

├── templates/ → HTML templates for UI

├── mini_hms/ → Main Django project settings and configuration

├── manage.py → Django project management script

---

# Installation Guide

Follow the steps below to run this project on your local system.

## Step 1: Clone the Repository

git clone https://github.com/iotiangyanu/Mini-hospital-management-system.git

cd Mini-hospital-management-system

---

## Step 2: Create a Virtual Environment

python -m venv venv

Activate the environment:

Windows:

venv\Scripts\activate

Linux / Mac:

source venv/bin/activate

---

## Step 3: Install Required Dependencies

pip install -r requirements.txt

---

## Step 4: Configure Database

Update database settings in:

mini_hms/settings.py

Example PostgreSQL configuration:

DATABASES = {
'default': {
'ENGINE': 'django.db.backends.postgresql',
'NAME': 'hms_db',
'USER': 'postgres',
'PASSWORD': 'your_password',
'HOST': 'localhost',
'PORT': '5432',
}
}

---

## Step 5: Run Migrations

python manage.py makemigrations

python manage.py migrate

---

## Step 6: Create Superuser (Admin)

python manage.py createsuperuser

Follow the instructions to create an admin account.

---

## Step 7: Run the Development Server

python manage.py runserver

Open your browser and visit:

http://127.0.0.1:8000/

---

# How the System Works

1. Users register as either **Doctor or Patient**.
2. Doctors create available **appointment slots**.
3. Patients view available slots and **book appointments**.
4. Once a slot is booked, it becomes unavailable.
5. Email notifications are sent to confirm registration and bookings.
6. Appointments can optionally be synchronized with **Google Calendar**.

---

# Future Improvements

Possible future enhancements include:

* Online payment integration
* Video consultation support
* Advanced admin dashboard
* Patient medical records management
* Doctor ratings and reviews
* Mobile application integration

---

# Learning Outcomes

This project demonstrates practical implementation of:

* Django web development
* User authentication systems
* Database management with PostgreSQL
* RESTful design concepts
* Appointment scheduling logic
* Third-party API integration
* Email automation

---

# Author

Developed by:

**Gyanesh Dwivedi**

Python Developer | Django Developer

---

# License

This project is developed for **educational and learning purposes**.


# How to Download and Run This Project

Follow these steps to download and run the project on your system.

## 1. Clone the Repository

Open your terminal or command prompt and run:

git clone https://github.com/iotiangyanu/Mini-hospital-management-system.git

This command downloads the project to your system.

---

## 2. Navigate to the Project Folder

cd Mini-hospital-management-system

---

## 3. Create a Virtual Environment

It is recommended to run the project inside a virtual environment.

python -m venv venv

Activate the virtual environment:

### Windows

venv\Scripts\activate

### Linux / macOS

source venv/bin/activate

---

## 4. Install Required Dependencies

Install all required Python packages using:

pip install -r requirements.txt

---

## 5. Configure the Database

Open the file:

mini_hms/settings.py

Update the database configuration with your PostgreSQL credentials.

Example configuration:

DATABASES = {
'default': {
'ENGINE': 'django.db.backends.postgresql',
'NAME': 'hms_db',
'USER': 'postgres',
'PASSWORD': 'your_password',
'HOST': 'localhost',
'PORT': '5432',
}
}

Make sure PostgreSQL is installed and running on your system.

---

## 6. Apply Database Migrations

Run the following commands to create database tables:

python manage.py makemigrations

python manage.py migrate

---

## 7. Create Admin User (Optional)

To access the Django admin panel:

python manage.py createsuperuser

Follow the instructions to create your admin credentials.

---

## 8. Run the Development Server

Start the Django development server:

python manage.py runserver

---

## 9. Open the Application

Open your browser and visit:

http://127.0.0.1:8000/

You should now see the **Mini Hospital Management System homepage**.

---

# Admin Panel

To access the admin dashboard, visit:

http://127.0.0.1:8000/admin/

Login using the superuser credentials you created earlier.

---

# Stopping the Server

To stop the server, press:

CTRL + C

