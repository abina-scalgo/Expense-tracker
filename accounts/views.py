from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from .pagination import CustomPagination 
from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    CustomTokenObtainPairSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    UserDeactivateSerializer
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


# List Users View
class UserListView(generics.ListAPIView):
    queryset = User.objects.filter(is_active=True).select_related('details').order_by('-created_at')
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination


# Combined View for GET (View) and PUT (Edit) and DELETE (Delete)
class UserDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all().select_related('details')
    permission_classes = [IsAdminUser]
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        if self.request.method == 'DELETE':
            return UserDeactivateSerializer
        return UserDetailSerializer

    def perform_destroy(self, instance):
        serializer = self.get_serializer(instance, data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()




