from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserDetails
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re
from django.contrib.auth.hashers import check_password

User = get_user_model()

# Custom Login Serializer (JWT)
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


# Registration Serializer
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


# Change Password Serializer
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user

        # Check if current password is correct
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        new_pass = attrs.get('new_password')
        old_pass = attrs.get('old_password')
        confirm_pass = attrs.get('confirm_password')

        # Check if new password is same as old password
        if new_pass == old_pass:
            raise serializers.ValidationError(
                {"new_password": "New Password cannot be same as your current password."}
            )

        # Check if new password is same as confirm password
        if new_pass != confirm_pass:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        # Validate that the password meets all security criteria
        rules = [
            len(new_pass) >= 8,                  
            re.search(r'[A-Z]', new_pass),       
            re.search(r'[a-z]', new_pass),       
            re.search(r'[0-9]', new_pass),       
            re.search(r'[!@#$%^&*()_+{}|:\"<>?]', new_pass)
        ]

        if not all(rules):
            raise serializers.ValidationError({
                "new_password": "Password must contain at least 8 characters, including uppercase, lowercase, numbers, and symbols."
            })

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.must_change_password = False 
        user.save()
        return user
