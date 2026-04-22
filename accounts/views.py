from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    CustomTokenObtainPairSerializer
)

# 1. LOGIN VIEW (JWT)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Handles user login and returns JWT tokens along with 
    custom flags like 'must_change_password' and 'role'.
    """
    serializer_class = CustomTokenObtainPairSerializer


#  REGISTRATION VIEW
class UserRegistrationView(generics.CreateAPIView):
    """
    Handles new user registration. Open to anyone (AllowAny).
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
