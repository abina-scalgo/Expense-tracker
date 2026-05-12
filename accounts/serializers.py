from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserDetails, BankDetails
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

User = get_user_model()

# Custom Login Serializer (JWT)
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
# Registration Serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    # Profile Fields
    password = serializers.CharField(write_only=True, min_length=8)
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
            user = User.objects.create_user(**validated_data)

        # Create the linked UserDetails profile
            UserDetails.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name
            )

            # Create Bank Record
            BankDetails.objects.create(user=user, **bank_data)

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

#Bankdetails Serializer
class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = [
            'id', 'account_number', 'ifsc_code', 'bank_name', 
            'account_holder_name', 'is_primary', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']