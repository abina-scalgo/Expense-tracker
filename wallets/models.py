from django.db import models
from django.conf import settings
import uuid

#Create your models here.

class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='wallet'
    )
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_redeemed = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pending_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)
    
    expense = models.ForeignKey(
        'expense.Expense', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='managed_wallets'
    )

    def __str__(self):
        return f"Wallet: {self.user.username}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'credit (expense approved)'),
        ('debit', 'debit (withdrawal processed)'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    
    expense = models.ForeignKey(
        'expense.Expense', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    

    withdrawal_id = models.UUIDField(null=True, blank=True) 

    type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
