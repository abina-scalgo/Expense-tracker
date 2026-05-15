from rest_framework import generics, status, viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import User, BankDetails
from .pagination import CustomPagination 
from .utils import send_password_reset_email
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

    # POST /admin/users -> Triggers live Mailgun delivery upon creation
    def perform_create(self, serializer):
        user = serializer.save()
        # Dispatches credentials via your Mailgun HTTP REST API channel
        send_password_reset_email(user.email, user.plain_password)



    # POST /admin/users/send-credentials -> Explicit administrative credential re-send
    @action(detail=False, methods=['post'], url_path='send-credentials')
    def send_credentials(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Target user email address is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Look up the employee target profile record
        user = get_object_or_404(User, email=email)

        # Securely generate reset parameters
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # Construct frontend application reset URL
        frontend_base_url = "mobilefrontend.com"
        reset_link = f"{frontend_base_url}/{uid}/{token}/"

        # Execute direct delivery transaction call via Mailgun API endpoint
        email_sent = send_password_reset_email(user.email, reset_link)

        if not email_sent:
            return Response(
                {"detail": "Reset token generated, but Mailgun server delivery failed."}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        return Response({
            "detail": f"Password reset link successfully dispatched to {user.email}.",
            "reset_link_generated": reset_link
        }, status=status.HTTP_200_OK)


    def perform_destroy(self, instance):
        # Soft delete as per requirements
        instance.is_active = False
        instance.save()


class ResetPasswordFromEmailView(generics.GenericAPIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not all([uidb64, token, new_password]):
            return Response(
                {"detail": "Fields 'uid', 'token', and 'new_password' are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid or corrupt link parameters."}, status=status.HTTP_400_BAD_REQUEST)
            
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "This reset link has expired or has already been used."}, status=status.HTTP_400_BAD_REQUEST)
            
        user.set_password(new_password)
        if hasattr(user, 'must_change_password'):
            user.must_change_password = False
        user.save()
        
        return Response({"detail": "Password updated successfully via email token."}, status=status.HTTP_200_OK)
