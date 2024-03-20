from rest_framework import serializers
from myapp.models import User
from myapp.utils import send_verification_email, generate_verification_token

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        verification_token = generate_verification_token()  # Implement your token generation logic
        user.verification_token = verification_token
        user.save()
        send_verification_email(user, verification_token)
        return user

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()
    otp = serializers.CharField(required=False)

class OTPVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField()

class UserPasswordResetSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ('email')

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'password')