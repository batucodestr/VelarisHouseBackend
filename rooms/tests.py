from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Room
from .serializers import (
    AdminRoomSerializer,
    KeyboxCodeSerializer,
    RoomDetailSerializer,
    RoomSerializer,
)


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


class RoomModelTestCase(APITestCase):
    def test_str_representation(self):
        room = make_room(room_number=205)
        self.assertEqual(str(room), "Room 205")

    def test_room_number_must_be_unique(self):
        make_room(room_number=101)
        with self.assertRaises(Exception):
            make_room(room_number=101)

    def test_is_active_defaults_to_true(self):
        room = make_room()
        self.assertTrue(room.is_active)


class RoomValidationMixinTestCase(APITestCase):
    def _valid_payload(self, **overrides):
        payload = {
            "room_number": 101,
            "room_type": "single",
            "price": "100.00",
            "capacity": 2,
            "is_active": True,
            "keybox_code": "1234",
        }
        payload.update(overrides)
        return payload

    def test_room_serializer_valid_data(self):
        serializer = RoomSerializer(data=self._valid_payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_room_number_must_be_positive(self):
        serializer = RoomSerializer(data=self._valid_payload(room_number=0))
        self.assertFalse(serializer.is_valid())
        self.assertIn("room_number", serializer.errors)

    def test_room_number_negative_is_invalid(self):
        serializer = RoomSerializer(data=self._valid_payload(room_number=-5))
        self.assertFalse(serializer.is_valid())
        self.assertIn("room_number", serializer.errors)

    def test_price_must_be_positive(self):
        serializer = RoomSerializer(data=self._valid_payload(price="0.00"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_price_negative_is_invalid(self):
        serializer = RoomSerializer(data=self._valid_payload(price="-10.00"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_capacity_must_be_positive(self):
        serializer = AdminRoomSerializer(data=self._valid_payload(capacity=0))
        self.assertFalse(serializer.is_valid())
        self.assertIn("capacity", serializer.errors)

    def test_keybox_code_must_be_numeric(self):
        serializer = KeyboxCodeSerializer(data=self._valid_payload(keybox_code="abcd"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("keybox_code", serializer.errors)

    def test_keybox_code_must_be_at_least_four_digits(self):
        serializer = KeyboxCodeSerializer(data=self._valid_payload(keybox_code="12"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("keybox_code", serializer.errors)

    def test_keybox_code_valid(self):
        serializer = KeyboxCodeSerializer(data=self._valid_payload(keybox_code="9876"))
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_admin_room_serializer_valid_data(self):
        serializer = AdminRoomSerializer(data=self._valid_payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_room_detail_serializer_has_no_validation_mixin(self):
        room = make_room()
        serializer = RoomDetailSerializer(instance=room)
        self.assertEqual(
            set(serializer.data.keys()),
            {"room_number", "room_type", "price", "capacity", "is_active"},
        )


class RoomListViewTestCase(APITestCase):
    def test_list_rooms_is_publicly_accessible(self):
        make_room(room_number=101)
        make_room(room_number=102)

        response = self.client.get(reverse("room-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_list_rooms_response_fields(self):
        make_room(room_number=101)

        response = self.client.get(reverse("room-list"))

        self.assertEqual(
            set(response.data["results"][0].keys()),
            {"room_number", "room_type", "price", "is_active"},
        )


class RoomDetailViewTestCase(APITestCase):
    def test_retrieve_room_is_publicly_accessible(self):
        room = make_room(room_number=101)

        response = self.client.get(reverse("room-detail", args=[room.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["room_number"], 101)

    def test_retrieve_nonexistent_room_returns_404(self):
        response = self.client.get(reverse("room-detail", args=[999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RoomCreateViewTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.regular_user = User.objects.create_user(
            username="regular", email="regular@example.com", password="userpass"
        )
        self.payload = {
            "room_number": 301,
            "room_type": "suite",
            "price": "250.00",
            "capacity": 4,
            "is_active": True,
            "keybox_code": "4321",
        }

    def test_unauthenticated_user_cannot_create_room(self):
        response = self.client.post(reverse("room-create"), self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_user_cannot_create_room(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(reverse("room-create"), self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_can_create_room(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(reverse("room-create"), self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Room.objects.filter(room_number=301).exists())

    def test_admin_cannot_create_room_with_invalid_keybox_code(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {**self.payload, "keybox_code": "abc"}
        response = self.client.post(reverse("room-create"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RoomRetrieveUpdateDestroyViewTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.regular_user = User.objects.create_user(
            username="regular", email="regular@example.com", password="userpass"
        )
        self.room = make_room(room_number=101)

    def test_unauthenticated_user_cannot_retrieve_room(self):
        response = self.client.get(reverse("room-update", args=[self.room.pk]))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_retrieve_room(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse("room-update", args=[self.room.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["room_number"], 101)

    def test_admin_can_update_room(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            reverse("room-update", args=[self.room.pk]), {"price": "150.00"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room.refresh_from_db()
        self.assertEqual(self.room.price, Decimal("150.00"))

    def test_non_admin_cannot_update_room(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(
            reverse("room-update", args=[self.room.pk]), {"price": "150.00"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_room(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(reverse("room-destroy", args=[self.room.pk]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Room.objects.filter(pk=self.room.pk).exists())

    def test_non_admin_cannot_delete_room(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(reverse("room-destroy", args=[self.room.pk]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Room.objects.filter(pk=self.room.pk).exists())
