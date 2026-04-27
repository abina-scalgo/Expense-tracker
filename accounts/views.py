from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    CustomTokenObtainPairSerializer,
    LogoutSerializer
)

# 1. LOGIN VIEW (JWT)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Handles user login and returns JWT tokens along with 
    custom flags like 'must_change_password' and 'role'.
    """
    serializer_class = CustomTokenObtainPairSerializer


# 2. REGISTRATION VIEW
class UserRegistrationView(generics.CreateAPIView):
    """
    Handles new user registration. Open to anyone (AllowAny).
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


# 3. LOGOUT VIEW
class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

