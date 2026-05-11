from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminRoleOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets, permissions
from .models import User, BankDetails
from .serializers import (
    UserRegistrationSerializer, 
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    BankDetailsSerializer
)

# Login View (JWT)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Registration View
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAdminRoleOrReadOnly]


# Logout View
class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

# Bankdetails View
class BankDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = BankDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Returns all bank accounts for logged-in employee
        return BankDetails.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user
        serializer.save(user=self.request.user)