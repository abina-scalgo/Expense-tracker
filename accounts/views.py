from django.core.mail import send_mail
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminRoleOrReadOnly
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets, permissions
from .models import User, BankDetails
from .pagination import CustomPagination 
from .serializers import (
    UserRegistrationSerializer, 
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    BankDetailsSerializer,
    UserListSerializer, UserDetailSerializer, UserUpdateSerializer
)

# Login View (JWT)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Change Password View
class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)

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

# User View
class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('details').order_by('-created_at')
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.filter(is_active=True)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create': return UserRegistrationSerializer
        if self.action == 'list': return UserListSerializer
        if self.action in ['update', 'partial_update']: return UserUpdateSerializer
        return UserDetailSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        
        send_mail(
            'Your Account Credentials',
            f'Email: {user.email}\nPassword: {user.plain_password}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

    def perform_destroy(self, instance):
        # Soft delete as per requirements
        instance.is_active = False
        instance.save()
