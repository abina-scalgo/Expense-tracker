import string
import secrets
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .pagination import CustomPagination 
from .serializers import (
    CustomTokenObtainPairSerializer, UserRegistrationSerializer,
    UserListSerializer, UserDetailSerializer, UserUpdateSerializer
)

# Login View (JWT)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('details').order_by('-created_at')
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'create': return UserRegistrationSerializer
        if self.action == 'list': return UserListSerializer
        if self.action in ['update', 'partial_update']: return UserUpdateSerializer
        return UserDetailSerializer

    def perform_create(self, serializer):
        # Auto-generate 12-char password
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        generated_password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        user = serializer.save(password=generated_password)
        user.must_change_password = True
        user.save()
        
        # Send Email
        send_mail(
            'Your Account Credentials',
            f'Email: {user.email}\nPassword: {generated_password}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
