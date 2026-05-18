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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user.email} | {self.type} | Read: {self.is_read}"
