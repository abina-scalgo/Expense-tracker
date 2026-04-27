from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserDetails
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

# CUSTOM LOGIN SERIALIZER (JWT)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Adds custom fields to the JWT response so the mobile app knows 
    the user's role and if they need to reset their password.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Injects extra data into the JSON response
        data['user_id'] = str(self.user.id)
        data['role'] = self.user.role
        data['must_change_password'] = self.user.must_change_password
        
        return data


# REGISTRATION SERIALIZER
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Creates a User and an associated UserDetails profile record simultaneously.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role', 'first_name', 'last_name']

    def create(self, validated_data):
        # Extract profile names before creating the user
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        
        # Create the User (the Manager handles hashing the password)
        user = User.objects.create_user(**validated_data)
        
        # Create the linked UserDetails profile
        UserDetails.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name
        )
        return user
