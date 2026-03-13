from django.contrib.auth.models import AbstractUser
from django.db import models


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
    REQUIRED_FIELDS = ["email", "full_name", "gender", "date_of_birth", "mobile_number"]

    # Doctor fields
    qualification = models.CharField(max_length=200, blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    experience_years = models.IntegerField(blank=True, null=True)
    license_number = models.CharField(max_length=200, blank=True, null=True)

    # Patient fields
    blood_group = models.CharField(max_length=5, blank=True, null=True)

    illness_description = models.TextField(blank=True, null=True)