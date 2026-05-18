import uuid
from django.db import models
from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# CUSTOM USER MANAGER
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('must_change_password', False)
        return self.create_user(email, password, **extra_fields)

# USERS TABLE
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
        ('both', 'Both'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    must_change_password = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

# USER DETAILS TABLE
class UserDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='details'
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    profile_photo = models.CharField(max_length=255, null=True, blank=True) 
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_details'
        verbose_name_plural = "User Details"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# BANK DETAILS TABLE
class BankDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bank_accounts'
    )
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    bank_name = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bank_details'
        verbose_name_plural = "Bank Details"

    def save(self, *args, **kwargs):
        # Clean data formats
        self.ifsc_code = self.ifsc_code.upper().strip()
        self.account_number = self.account_number.strip()

        # If user has no existing bank accounts, force this one to be primary
        if not BankDetails.objects.filter(user=self.user).exists():
            self.is_primary = True

        if self.is_primary:
            with transaction.atomic():
                # Clear primary flag on OTHER accounts only excludes current ID
                queryset = BankDetails.objects.filter(user=self.user, is_primary=True)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
                queryset.update(is_primary=False)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        user = self.user
        was_primary = self.is_primary

        with transaction.atomic():
            super().delete(*args, **kwargs)
            
            if was_primary:
                next_account = BankDetails.objects.filter(user=user).order_by('created_at').first()
                if next_account:
                    BankDetails.objects.filter(pk=next_account.pk).update(is_primary=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"
