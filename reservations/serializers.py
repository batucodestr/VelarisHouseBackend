from rest_framework import serializers
from .models import Reservation


class ReservationCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = [
            "room",
            "check_in",
            "check_out",
        ]

class ReservationSerializer(serializers.ModelSerializer):

    keybox_code = serializers.CharField(
        source="room.keybox_code",
        read_only=True
    )

    class Meta:
        model = Reservation
        fields = [
            "id",
            "user",
            "room",
            "check_in",
            "check_out",
            "status",
            "keybox_code",
        ]