from rest_framework import serializers
from .models import Wallet, Transaction

class WalletSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['available_balance', 'total_redeemed', 'pending_amount', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'type', 'amount', 'description', 'expense', 'withdrawal_id', 'created_at']