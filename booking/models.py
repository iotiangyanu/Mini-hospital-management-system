from django.db import models
from django.conf import settings
from doctors.models import Availability

User = settings.AUTH_USER_MODEL


class Booking(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
    )

    patient = models.ForeignKey(User, on_delete=models.CASCADE)

    slot = models.OneToOneField(Availability, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient} booked {self.slot} - {self.status}"


class RejectedBooking(models.Model):
    """
    Tracks which patients were rejected for which slots.
    These slots should be hidden from the rejected patient but visible to others.
    """
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(Availability, on_delete=models.CASCADE)
    rejected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'slot')

    def __str__(self):
        return f"{self.patient} rejected for {self.slot}"


class CancelledBooking(models.Model):
    """
    Tracks which patients cancelled which slots.
    These slots should be hidden from the cancelling patient but visible to others.
    """
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(Availability, on_delete=models.CASCADE)
    cancelled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'slot')

    def __str__(self):
        return f"{self.patient} cancelled {self.slot}"