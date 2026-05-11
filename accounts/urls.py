from django.urls import path
from .views import UserRegistrationView, CustomTokenObtainPairView, ChangePasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    # Essential for mobile: allows the app to get a new access token 
    # without making the user type their password again.
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
