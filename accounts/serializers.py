from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserDetails, BankDetails
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
import re
import string
import secrets
from django.contrib.auth.hashers import check_password

User = get_user_model()


# Custom Login Serializer (JWT)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    #Adds custom fields to the JWT response to determine if they need to reset their password.
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id'] = str(self.user.id)
        data['role'] = self.user.role
        data['must_change_password'] = self.user.must_change_password
        return data


# Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    # Profile Fields
    password = serializers.CharField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    
    # Bank Fields
    account_number = serializers.CharField(write_only=True)
    ifsc_code = serializers.CharField(write_only=True)
    bank_name = serializers.CharField(write_only=True)
    account_holder_name = serializers.CharField(write_only=True)
    

    class Meta:
        model = User
        fields = [
            'email', 'password', 'role', 
            'first_name', 'last_name',
            'account_number', 'ifsc_code', 'bank_name', 'account_holder_name'
        ]

    def create(self, validated_data):
        # Generate a UNIQUE password
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        generated_password = ''.join(secrets.choice(alphabet) for i in range(12))
        # Pop out data for associated tables
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        
        bank_data = {
            'account_number': validated_data.pop('account_number'),
            'ifsc_code': validated_data.pop('ifsc_code'),
            'bank_name': validated_data.pop('bank_name'),
            'account_holder_name': validated_data.pop('account_holder_name'),
            'is_primary': True  # Default first bank account to primary
        }

        # Use a transaction to ensure all-or-nothing creation
        with transaction.atomic():
            # Create User
            user = User.objects.create_user(
                password=generated_password, 
                **validated_data
            )
            user.must_change_password = True
            user.save()
        # Create the linked UserDetails profile
            UserDetails.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name
            )

            # Create Bank Record
            BankDetails.objects.create(user=user, **bank_data)
            user.plain_password = generated_password

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


# Logout Serializer
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            refresh_token = attrs["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            raise serializers.ValidationError("Invalid or expired token.")
            
        return attrs


# Bank Details Serializer
class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = [
            'id', 'account_number', 'ifsc_code', 'bank_name', 
            'account_holder_name', 'is_primary', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# List User Serializer
class UserListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='details.first_name', read_only=True)
    last_name = serializers.CharField(source='details.last_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'first_name', 'last_name', 'is_active', 'must_change_password', 'created_at']


#View User Serializer
class UserDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='details.first_name', read_only=True)
    last_name = serializers.CharField(source='details.last_name', read_only=True)
    phone_number = serializers.CharField(source='details.phone_number', read_only=True)
    designation = serializers.CharField(source='details.designation', read_only=True)
    profile_photo = serializers.CharField(source='details.profile_photo', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'first_name', 'last_name', 'phone_number', 'designation', 'profile_photo', 'is_active', 'is_staff', 'must_change_password', 'created_at', 'updated_at']


#Update User Serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='details.first_name')
    last_name = serializers.CharField(source='details.last_name')
    phone_number = serializers.CharField(source='details.phone_number', required=False)
    designation = serializers.CharField(source='details.designation', required=False)

    class Meta: 
        model = User
        fields = ['role', 'first_name', 'last_name', 'phone_number', 'designation']

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', {})
        
        # Update User
        instance.role = validated_data.get('role', instance.role)
        instance.save()

        # Update UserDetails
        details = instance.details
        for attr, value in details_data.items():
            setattr(details, attr, value)
        details.save()
        return instance