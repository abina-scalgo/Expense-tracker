from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserDetails
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id'] = str(self.user.id)
        data['role'] = self.user.role
        data['must_change_password'] = self.user.must_change_password
        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'role', 'first_name', 'last_name']

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        user = User.objects.create_user(**validated_data)
        UserDetails.objects.create(user=user, first_name=first_name, last_name=last_name)
        return user

class UserListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='details.first_name', read_only=True)
    last_name = serializers.CharField(source='details.last_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'first_name', 'last_name', 'is_active', 'must_change_password', 'created_at']

class UserDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='details.first_name', read_only=True)
    last_name = serializers.CharField(source='details.last_name', read_only=True)
    phone_number = serializers.CharField(source='details.phone_number', read_only=True)
    designation = serializers.CharField(source='details.designation', read_only=True)
    profile_photo = serializers.CharField(source='details.profile_photo', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'first_name', 'last_name', 'phone_number', 'designation', 'profile_photo', 'is_active', 'is_staff', 'must_change_password', 'created_at', 'updated_at']

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
