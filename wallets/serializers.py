from rest_framework import serializers
from .models import Wallet, Transaction, WithdrawalRequest

class WalletSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['available_balance', 'total_redeemed', 'pending_amount', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'type', 'amount', 'description', 'withdrawal_id', 'created_at']

class WithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = ['id', 'amount', 'status', 'bank_detail', 'requested_at', 'processed_at', 'failure_reason']
