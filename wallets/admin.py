from django.contrib import admin
from .models import Wallet, Transaction

# Register your models here.

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'available_balance', 'total_redeemed', 'pending_amount', 'updated_at')
    actions = None 

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'type', 'amount', 'created_at')
    list_filter = ('type',)
    actions = None
