from django.urls import path
from myapp.views import RegisterView, LoginInitiateView, LoginVerifyView, UserProfileAPIView, UserProfileDetailAPIView, UserPasswordResetView, PasswordResetRequestView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginInitiateView.as_view(), name = 'login'),
    path('verify-otp/', LoginVerifyView.as_view(), name='verify-otp'),
    path('profile/', UserProfileAPIView.as_view(), name="profile"),
    path('profile/<int:pk>/', UserProfileDetailAPIView.as_view(), name='profile-detail'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('reset-password/<uuid:token>/', UserPasswordResetView.as_view(), name='password_reset')
]
