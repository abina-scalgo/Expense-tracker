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
        help_text="Scheduled time for Celery to check/auto-process"
    )
    actioned_at = models.DateTimeField(
        blank=True, 
        null=True, 
        help_text="Timestamp when an admin manually took action"
    )
    
    # Audit Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expenses'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.amount} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Check if this is a brand new record being created
        if self._state.adding: 
            # Set the deadline for 24 hours from the moment of creation
            if not self.approve_or_rejected_at:
                self.approve_or_rejected_at = timezone.now() + timedelta(hours=24)
                
        super().save(*args, **kwargs)