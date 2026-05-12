from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from .models import ExpenseCategory
from rest_framework.viewsets import ModelViewSet
from .models import ExpenseCategory, Expense
from .serializers import ExpenseCategorySerializer, ExpenseSerializer
from .permissions import IsAdminRoleOrReadOnly
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.decorators import action
from django.db import transaction
from wallets.models import Wallet, Transaction

# Create your views here.

#Add the expense category
class ExpenseCategoryViewSet(ModelViewSet):
    # queryset = ExpenseCategory.objects.all().order_by('-created_at')
    queryset = ExpenseCategory.objects.filter(is_active=True)
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminRoleOrReadOnly]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        return "deleted successfully"

# Expense ViewSet
class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'category', 'expense_date']

    def get_queryset(self):
        # Restriction: Employees only see their own expenses
        return Expense.objects.filter(user=self.request.user).prefetch_related('receipts')

    def perform_create(self, serializer):
        # Automatically assign the logged-in user
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Rule: Only editable if status is pending
        if instance.status != Expense.Status.PENDING:
            return Response(
                {"detail": "Cannot edit an expense after it has been actioned."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Rule: Only deletable if status is pending
        if instance.status != Expense.Status.PENDING:
            return Response(
                {"detail": "Cannot delete an expense after it has been actioned."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class AdminExpenseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Expense.objects.all().select_related('user', 'category')
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAdminUser]

    #Expense Approve
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        expense = self.get_object()
        
        if expense.status != Expense.Status.PENDING:
            return Response({"detail": "Only pending expenses can be approved."}, status=400)

        with transaction.atomic():
            # Update Expense
            expense.status = Expense.Status.APPROVED
            expense.actioned_at = timezone.now()
            expense.save()

            # Update Wallet (Crediting the user)
            wallet, created = Wallet.objects.get_or_create(user=expense.user)
            wallet.available_balance += expense.amount # Add to balance
            wallet.save()

            # Create Transaction Record
            Transaction.objects.create(
                wallet=wallet,
                expense=expense,
                type='credit',
                amount=expense.amount,
                description=f"Reimbursement for {expense.category}"
            )

        return Response({"detail": "Expense approved and balance updated."})

    #Expense Reject
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        expense = self.get_object()
        
        # Check if remarks were provided
        remarks = request.data.get('remarks')
        if not remarks:
            return Response({"remarks": "This field is mandatory for rejection."}, status=400)

        if expense.status != Expense.Status.PENDING:
            return Response({"detail": "Only pending expenses can be rejected."}, status=400)

        expense.status = Expense.Status.REJECTED
        expense.actioned_at = timezone.now()
        # Append remarks to the note
        expense.note = f"{expense.note or ''}\n\nAdmin Remarks: {remarks}".strip()
        expense.save()

        return Response({"detail": "Expense rejected successfully."})
