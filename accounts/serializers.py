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


#List Users Serializer
class UserListSerializer(serializers.ModelSerializer):
    # Fetch profile details from the related 'details' model
    first_name = serializers.CharField(source='details.first_name', read_only=True)
    last_name = serializers.CharField(source='details.last_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'first_name', 'last_name', 'is_active', 'must_change_password', 'created_at']


# View User Serializer
class UserDetailSerializer(serializers.ModelSerializer):
    # Fetch profile details from the related 'details' model
    first_name = serializers.CharField(source='details.first_name', read_only=True)
    last_name = serializers.CharField(source='details.last_name', read_only=True)
    phone_number = serializers.CharField(source='details.phone_number', read_only=True)
    designation = serializers.CharField(source='details.designation', read_only=True)
    profile_photo = serializers.CharField(source='details.profile_photo', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'role', 'first_name', 'last_name', 
            'phone_number', 'designation', 'profile_photo',
            'is_active', 'is_staff', 'must_change_password', 
            'created_at', 'updated_at'
        ]


# Edit User Serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    # Fetch profile details from the related 'details' model
    first_name = serializers.CharField(source='details.first_name')
    last_name = serializers.CharField(source='details.last_name')
    phone_number = serializers.CharField(source='details.phone_number')
    designation = serializers.CharField(source='details.designation')

    class Meta: 
        model = User
        fields = ['role', 'is_active', 'first_name', 'last_name', 'phone_number', 'designation']

    def update(self, instance, validated_data):
        
        details_data = validated_data.pop('details', {})
        
        # Update User Table
        instance.role = validated_data.get('role', instance.role)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()

        # Update UserDetails Table
        details = instance.details
        details.first_name = details_data.get('first_name', details.first_name)
        details.last_name = details_data.get('last_name', details.last_name)
        details.phone_number = details_data.get('phone_number', details.phone_number)
        details.designation = details_data.get('designation', details.designation)
        details.save()

        return instance


# Deactivate User Serializer
class UserDeactivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [] 

    def update(self, instance, validated_data):
        # Logic: Perform the soft delete
        instance.is_active = False
        instance.save()
        return instance