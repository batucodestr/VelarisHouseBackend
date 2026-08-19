from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from rooms.models import Room

from .models import Reservation


def make_room(**overrides):
    defaults = {
        "room_number": 101,
        "keybox_code": "1234",
        "room_type": "single",
        "price": Decimal("100.00"),
        "capacity": 2,
        "is_active": True,
    }
    defaults.update(overrides)
    return Room.objects.create(**defaults)


def make_reservation(user, room, **overrides):
    defaults = {
        "user": user,
        "room": room,
        "check_in": date(2026, 1, 10),
        "check_out": date(2026, 1, 15),
        "status": "active",
    }
    defaults.update(overrides)
    return Reservation.objects.create(**defaults)


class ReservationModelTestCase(APITestCase):
    def test_str_representation(self):
        user = User.objects.create_user(username="alice", password="pass12345")
        room = make_room(room_number=205)
        reservation = make_reservation(user, room)

        self.assertEqual(str(reservation), "alice - Room 205")

    def test_status_defaults_to_active(self):
        user = User.objects.create_user(username="alice", password="pass12345")
        room = make_room()
        reservation = Reservation.objects.create(
            user=user, room=room, check_in=date(2026, 1, 10), check_out=date(2026, 1, 15)
        )

        self.assertEqual(reservation.status, "active")


class ReservationListViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")
        self.other_user = User.objects.create_user(username="bob", password="pass12345")
        self.staff_user = User.objects.create_user(
            username="staff", password="pass12345", is_staff=True
        )
        self.room = make_room(room_number=101, keybox_code="1234")
        self.own_reservation = make_reservation(self.user, self.room)
        self.other_reservation = make_reservation(
            self.other_user,
            make_room(room_number=102),
            check_in=date(2026, 2, 1),
            check_out=date(2026, 2, 5),
        )

    def test_unauthenticated_user_cannot_list_reservations(self):
        response = self.client.get(reverse("reservation-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_sees_only_own_reservations(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("reservation-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.own_reservation.id)
        self.assertEqual(results[0]["keybox_code"], "1234")

    def test_staff_user_sees_all_reservations(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(reverse("reservation-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)


class ReservationCreateViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")
        self.room = make_room(room_number=101)
        self.client.force_authenticate(user=self.user)

    def _payload(self, **overrides):
        payload = {
            "room": self.room.pk,
            "check_in": "2026-03-01",
            "check_out": "2026-03-05",
        }
        payload.update(overrides)
        return payload

    def test_unauthenticated_user_cannot_create_reservation(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse("reservation-create"), self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_reservation(self):
        response = self.client.post(reverse("reservation-create"), self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data.keys()), {"room", "check_in", "check_out"}
        )
        reservation = Reservation.objects.get()
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.room, self.room)
        self.assertEqual(reservation.status, "active")

    def test_create_ignores_client_supplied_user(self):
        other_user = User.objects.create_user(username="mallory", password="pass12345")
        response = self.client.post(
            reverse("reservation-create"),
            self._payload(user=other_user.pk),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reservation = Reservation.objects.get()
        self.assertEqual(reservation.user, self.user)

    def test_cannot_reserve_inactive_room(self):
        inactive_room = make_room(room_number=102, is_active=False)
        response = self.client.post(
            reverse("reservation-create"),
            self._payload(room=inactive_room.pk),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Reservation.objects.exists())

    def test_user_cannot_have_two_active_reservations(self):
        make_reservation(self.user, self.room, check_in=date(2026, 1, 1), check_out=date(2026, 1, 5))
        other_room = make_room(room_number=102)

        response = self.client.post(
            reverse("reservation-create"),
            self._payload(room=other_room.pk),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_cannot_create_overlapping_reservation_for_same_room(self):
        other_user = User.objects.create_user(username="bob", password="pass12345")
        make_reservation(
            other_user, self.room, check_in=date(2026, 3, 2), check_out=date(2026, 3, 8)
        )

        response = self.client.post(reverse("reservation-create"), self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Reservation.objects.count(), 1)

    def test_can_create_reservation_for_non_overlapping_dates(self):
        other_user = User.objects.create_user(username="bob", password="pass12345")
        make_reservation(
            other_user, self.room, check_in=date(2026, 1, 1), check_out=date(2026, 1, 5)
        )

        response = self.client.post(reverse("reservation-create"), self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 2)

    def test_cancelled_reservation_does_not_block_overlapping_dates(self):
        other_user = User.objects.create_user(username="bob", password="pass12345")
        make_reservation(
            other_user,
            self.room,
            check_in=date(2026, 3, 1),
            check_out=date(2026, 3, 10),
            status="cancelled",
        )

        response = self.client.post(reverse("reservation-create"), self._payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ReservationRetrieveDestroyViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")
        self.other_user = User.objects.create_user(username="bob", password="pass12345")
        self.staff_user = User.objects.create_user(
            username="staff", password="pass12345", is_staff=True
        )
        self.room = make_room(room_number=101, keybox_code="1234")
        self.reservation = make_reservation(self.user, self.room)

    def _url(self):
        return reverse("reservation-detail", args=[self.reservation.pk])

    def test_unauthenticated_user_cannot_retrieve_reservation(self):
        response = self.client.get(self._url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_retrieve_own_reservation(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self._url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.reservation.id)
        self.assertEqual(response.data["keybox_code"], "1234")

    def test_other_user_cannot_retrieve_reservation(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self._url())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_can_retrieve_any_reservation(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self._url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_is_not_supported(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self._url(), {"status": "cancelled"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_owner_can_delete_own_reservation(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self._url())

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Reservation.objects.filter(pk=self.reservation.pk).exists())

    def test_other_user_cannot_delete_reservation(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self._url())

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Reservation.objects.filter(pk=self.reservation.pk).exists())
