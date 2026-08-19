from django.shortcuts import render


from rest_framework.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from .models import Reservation
from .serializers import ReservationSerializer, ReservationCreateSerializer

from django.db import transaction
from django.utils import timezone
from rooms.models import Room

from django.contrib.auth.models import User
# Create your views here.


def auto_complete_reservations():
    """Flip any 'active' reservation whose check_out date has passed to 'completed'.

    There's no background scheduler in this project, so this runs lazily on
    every read — cheap enough for this dataset, and it keeps `status` correct
    before it's ever read (list/detail) or relied upon (the "one active
    reservation per user" rule in ReservationCreateView.perform_create).
    """
    Reservation.objects.filter(
        status="active", check_out__lt=timezone.localdate()
    ).update(status="completed")


class ReservationListView(generics.ListAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        auto_complete_reservations()
        user = self.request.user
        qs = Reservation.objects.all() if user.is_staff else Reservation.objects.filter(user=user)
        return qs.order_by("-created_at")

class ReservationCreateView(generics.CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = ReservationSerializer(serializer.instance)
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def perform_create(self, serializer):

        auto_complete_reservations()

        room = serializer.validated_data["room"]
        check_in = serializer.validated_data["check_in"]
        check_out = serializer.validated_data["check_out"]

        # Kullanıcıyı da kilitliyoruz.
        # Çünkü bir kullanıcının yalnızca 1 aktif rezervasyonu olabilir.
        user = User.objects.select_for_update().get(
            pk=self.request.user.pk
        )

        room = Room.objects.select_for_update().get(
            pk=room.pk
        )

        if not room.is_active:
            raise ValidationError(
                "This room is not available for reservation."
            )

        if Reservation.objects.filter(user=user,status="active").exists():
            raise ValidationError(
                "You already have an active reservation."
            )

        overlapping = Reservation.objects.filter(
            room=room,
            status="active",
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists()

        if overlapping:
            raise ValidationError(
                "Bu tarihler arasında oda müsait değil."
            )

        serializer.save(
            user=user,
            room=room,
            status="active"
        )

class ReservationRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        auto_complete_reservations()
        user = self.request.user
        if user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(user=user)
