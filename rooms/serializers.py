from rest_framework import serializers
from .models import Room
from .validations import RoomValidationMixin

class RoomSerializer(RoomValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'slug', 'room_number', 'room_type', 'price', 'capacity',
            'short_description', 'size_sqm', 'image_url', 'is_active',
        ]

class RoomDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'slug', 'room_number', 'room_type', 'price', 'capacity',
            'short_description', 'description', 'size_sqm', 'bed_type',
            'amenities', 'image_url', 'gallery', 'is_active',
        ]

class KeyboxCodeSerializer(RoomValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['room_number', 'keybox_code']

class AdminRoomSerializer(RoomValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'slug', 'room_number', 'room_type', 'price', 'capacity',
            'short_description', 'description', 'size_sqm', 'bed_type',
            'amenities', 'image_url', 'gallery', 'is_active', 'keybox_code',
        ]
        read_only_fields = ['slug']
