from django.db import models
from django.contrib.auth.models import User

from rooms.models import Room


class Reservation(models.Model):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    check_in = models.DateField()
    check_out = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Room {self.room.room_number}"