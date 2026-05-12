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
