from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from myapp.models import User
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from myapp.models import PasswordResetToken
from myapp.serializers import UserSerializer, UserPasswordResetSerializer, UserProfileSerializer
from myapp.utils import generate_otp, send_otp_via_infobip
from mypro.settings import FRONTEND_URL

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginInitiateView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        user = authenticate(request, username=phone_number, password=password)
        if user is not None:
            login(request, user)
            return Response({'message': 'Login successful'})
        else:
            otp = generate_otp()
            print(otp)
            send_otp_via_infobip(phone_number, otp)
            request.session['otp'] = otp
            return Response({'message': 'OTP sent'})

class LoginVerifyView(APIView):
    def post(self, request):
        otp = request.data.get('otp')
        stored_otp = request.session.get('otp')
        if otp == stored_otp:
            phone_number = request.session.get('phone_number')
            user = authenticate(request, username=phone_number)
            if user is not None:
                login(request, user)
                return Response({'message': 'Login successful'})
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileAPIView(APIView):
    def get(self, request):
        profiles = User.objects.all()
        serializer = UserProfileSerializer(profiles, many=True)
        return Response(serializer.data)
    
class UserProfileDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        profile = self.get_object(pk)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, pk):
        profile = self.get_object(pk)
        serializer = UserProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        print(email)
        if email:
            serializer = UserPasswordResetSerializer(data={'email': email})  # Create serializer instance with email
            if serializer.is_valid():
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
                token = PasswordResetToken.objects.create(user=user)
                reset_link = f"{settings.FRONTEND_URL}/reset-password/{token.token}"
                send_mail(
                    'Password Reset',
                    f'Click the following link to reset your password: {reset_link}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                return Response({"message": "Password reset link has been sent to your email."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Email field is required."}, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordResetView(APIView):
    def get(self, request, token):
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if reset_token.created_at < timezone.now() - timezone.timedelta(days=1):
                return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)
            user = reset_token.user
            new_password = User.objects.make_random_password()
            user.password = make_password(new_password)
            user.save()
            reset_token.delete()
            return redirect(settings.FRONTEND_URL + '/password-reset-success')
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Token does not exist'}, status=status.HTTP_404_NOT_FOUND)
