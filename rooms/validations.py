from rest_framework import serializers


class RoomValidationMixin:
    def validate_room_number(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Room number must be a positive integer."
            )
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be a positive number."
            )
        return value

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Capacity must be a positive integer."
            )
        return value

    def validate_keybox_code(self, value):
        if not str(value).isdigit():
            raise serializers.ValidationError(
                "Keybox code must be numeric."
            )

        if len(str(value)) < 4:
            raise serializers.ValidationError(
                "Keybox code must be at least 4 characters long."
            )

        return value
