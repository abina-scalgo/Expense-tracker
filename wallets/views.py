from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Wallet, Transaction, WithdrawalRequest
from .serializers import WalletSummarySerializer, TransactionSerializer
from decimal import Decimal
from django.db import transaction

# Create your views here.

class WalletViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure employees only see their own records
        return Wallet.objects.filter(user=self.request.user)

    # GET /wallet
    def list(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSummarySerializer(wallet)
        return Response(serializer.data)

    # GET /wallet/transactions
    @action(detail=False, methods=['get'], url_path='transactions')
    def transactions(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        transactions = wallet.transactions.all()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='withdraw')
    def withdraw(self, request):
        amount_str = request.data.get('amount')
        bank_detail_id = request.data.get('bank_detail_id')
        
        if not amount_str or not bank_detail_id:
            return Response({"detail": "Amount and bank_detail_id are required."}, status=400)
            
        try:
            amount = Decimal(str(amount_str))
        except:
            return Response({"detail": "Invalid amount format."}, status=400)

        if amount <= 0:
            return Response({"detail": "Amount must be greater than zero."}, status=400)

        wallet, _ = Wallet.objects.get_or_create(user=request.user)

        if wallet.available_balance < amount:
            return Response({"detail": "Insufficient available balance."}, status=400)

        with transaction.atomic():
            # Lock the wallet row for safety against concurrent requests
            wallet = Wallet.objects.select_for_update().get(id=wallet.id)
            
            # Update balances
            wallet.available_balance -= amount
            wallet.pending_amount += amount
            wallet.save()

            # Create the ACTUAL WithdrawalRequest record
            withdrawal_req = WithdrawalRequest.objects.create(
                wallet=wallet,
                bank_detail_id=bank_detail_id,
                amount=amount,
                status='pending'
            )

            # Create the Transaction record  
            Transaction.objects.create(
                wallet=wallet,
                type='debit',
                amount=amount,
                description="Withdrawal request initiated (held)",
                withdrawal_id=withdrawal_req.id
            )

        return Response({
            "detail": "Withdrawal initiated successfully. Balance is now held.",
            "withdrawal_id": withdrawal_req.id
        }, status=201)


    @action(detail=False, methods=['get'], url_path='withdrawals')
    def withdrawals(self, request):
        # Returns a list of all past withdrawal requests (debit types).
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        # Filter for 'debit' to show only withdrawals
        withdrawal_history = wallet.transactions.filter(type='debit').order_by('-created_at')
        serializer = TransactionSerializer(withdrawal_history, many=True)
        return Response(serializer.data)
