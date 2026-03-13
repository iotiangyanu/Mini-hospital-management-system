from django.db import models
from django.conf import settings
from doctors.models import Availability

User = settings.AUTH_USER_MODEL


class Booking(models.Model):

    patient = models.ForeignKey(User, on_delete=models.CASCADE)

    slot = models.OneToOneField(Availability, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    is_canceled_by_doctor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patient} booked {self.slot}"