from django.db import models
import uuid
from django.conf import settings 
from datetime import timedelta
from django.utils import timezone

# Create your models here.

class ExpenseCategory(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'expense_categories'
        ordering = ['name']
        verbose_name_plural = 'Expense Categories'

    def __str__(self):
        return self.name
    

#Expenses Table
class Expense(models.Model):
    # Status constants
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        AUTO_APPROVED = 'auto_approved', 'Auto Approved'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='expenses'
    )
    category = models.ForeignKey(
        'ExpenseCategory', 
        on_delete=models.PROTECT, # Prevents deleting categories that have expenses
        related_name='expenses'
    )

    # Core Fields
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=15, 
        choices=Status.choices,     
        default=Status.PENDING
    )
    expense_date = models.DateField()

    # Timing and Automation
    approve_or_rejected_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when an admin manually approved or rejected"
    )

    auto_approve_at = models.DateTimeField(
        help_text="Scheduled time for Celery to check/auto-process"
    )

    is_amount_auto_approved = models.BooleanField(
        default=False,
        help_text="True if expense amount was below AUTO_APPROVE_AMOUNT_LIMIT"
    )

    actioned_at = models.DateTimeField(
        blank=True, 
        null=True, 
        help_text="Timestamp when an admin manually took action"
    )
    
    # Audit Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    actioned_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    related_name='actioned_expenses',
    help_text="Admin who approved/rejected the expense. NULL for auto approvals."
    )

    class Meta:
        db_table = 'expenses'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.amount} ({self.status})"
    
    def save(self, *args, **kwargs):
        if self._state.adding: 
            if not self.auto_approve_at:
                try:
                    from core.models import SystemSettings
                    setting = SystemSettings.objects.get(key='AUTO_APPROVE_HOURS')
                    hours = int(setting.value)
                except Exception:
                    hours = 24  # Fallback safety default
                
                self.auto_approve_at = timezone.now() + timedelta(hours=hours)
                
        super().save(*args, **kwargs)



def expense_receipt_path(instance, filename):
    # Returns: receipts/<user_id>/<expense_id>/<filename>
    return f'receipts/{instance.expense.user.id}/{instance.expense.id}/{filename}'

class ExpenseReceipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(
        'Expense', 
        on_delete=models.CASCADE, 
        related_name='receipts'
    )
    
    file = models.FileField(upload_to=expense_receipt_path)
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)
    file_size_kb = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'expense_receipts'

    def __str__(self):
        return self.file_name

