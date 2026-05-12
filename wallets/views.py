from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Wallet, Transaction
from .serializers import WalletSummarySerializer, TransactionSerializer

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