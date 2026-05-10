from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):

    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    full_name = models.CharField(max_length=200)

    gender = models.CharField(max_length=10)

    date_of_birth = models.DateField()

    mobile_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True, blank=True)
    REQUIRED_FIELDS = ["email", "full_name", "gender", "date_of_birth", "mobile_number"]

    # Doctor fields
    qualification = models.CharField(max_length=200, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    practicing_year_from = models.IntegerField(blank=True, null=True)
    license_number = models.CharField(max_length=200, blank=True, null=True)

    # Patient fields
    blood_group = models.CharField(max_length=5, blank=True, null=True)

    @property
    def experience(self):
        if self.practicing_year_from:
            current_year = timezone.now().year
            experience = current_year - self.practicing_year_from
            return experience if experience >= 0 else 0
        return None

    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            age = today.year - self.date_of_birth.year
            if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
                age -= 1
            return age if age >= 0 else 0
        return None


class TemporaryRegistration(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128)  # hashed password
    otp = models.CharField(max_length=6)
    otp_created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10)
    full_name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    mobile_number = models.CharField(max_length=15)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    practicing_year_from = models.IntegerField(blank=True, null=True)
    license_number = models.CharField(max_length=200, blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)