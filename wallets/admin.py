from django.contrib import admin
from .models import Wallet, Transaction, WithdrawalRequest

# Register your models here.

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'available_balance', 'total_redeemed', 'pending_amount', 'updated_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('id', 'updated_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'type', 'amount', 'created_at')
    list_filter = ('type',)
    search_fields = ('wallet__user__email',)

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_wallet_user', 'amount', 'status', 'requested_at')
    list_filter = ('status',)
    readonly_fields = ('id', 'requested_at')
    
    # Helper to show user email instead of just Wallet UUID in the list
    def get_wallet_user(self, obj):
        return obj.wallet.user.email
    get_wallet_user.short_description = 'User'