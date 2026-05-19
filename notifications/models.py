import uuid
from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('new_expense', 'New Expense Submitted'),
        ('expense_approved', 'Expense Approved'),
        ('expense_rejected', 'Expense Rejected'),
        ('expense_auto_approved', 'Expense Auto Approved'),
        ('withdrawal_success', 'Withdrawal Processed Successfully'),
        ('withdrawal_failed', 'Withdrawal Procesing Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=100)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    fcm_sent = models.BooleanField(
        default=False,
        help_text="True if FCM notification was successfully delivered"
    )
    fcm_sent_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when the FCM push was sent successfully"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user.email} | {self.type} | Read: {self.is_read}"
    

class FcmTokens(models.Model):
    DEVICE_TYPE_CHOICES = (
        ('android', 'Android'),
        ('ios', 'iOS'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fcm_tokens'
    )
    token = models.TextField()
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPE_CHOICES, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fcm_tokens'
        verbose_name = 'Fcm Token'

    def __str__(self):
        return f"{self.user} - {self.device_type or 'Unknown'}"
