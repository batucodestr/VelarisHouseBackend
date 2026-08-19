from rest_framework import serializers
from .models import User, UserProfile

class RegisterSerializer(serializers.ModelSerializer):

    phone_number = serializers.CharField(write_only=True, allow_blank=False, required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username','email','password','phone_number']

    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')

        user = User.objects.create_user(
            **validated_data
        )

        UserProfile.objects.create(
            user=user,
            phone_number=phone_number
        )

        return user

    def validate_phone_number(self, value):
        if value == "":
            raise serializers.ValidationError(
                "Telefon numarası zorunludur!",
            )

        return value