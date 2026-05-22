from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from expense.models import Expense
from rest_framework import status
from wallets.models import Transaction, WithdrawalRequest


class AdminReportsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]


    # GET /admin/reports/expense-summary 
    @action(detail=False, methods=['get'], url_path='expense-summary')
    def expense_summary(self, request):

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                return Response({"error": "Invalid date range: Start date must be before the end date."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Expense.objects.all()

        if start_date:
            queryset = queryset.filter(expense_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(expense_date__lte=end_date)    


        # Expense grouped by status
        status_summary = queryset.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )

        # Expense grouped by category
        category_summary = queryset.values('category__name').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('-total_amount')

        # Expenses grouped by employee
        employee_summary = queryset.values('user__id', 'user__email').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('-total_amount')

        total_expenses = queryset.aggregate(
            total=Sum('amount')
        )['total'] or 0

        return Response({
            "total_expenses": total_expenses,
            "by_status": status_summary,
            "by_category": category_summary,
            "by_employee": employee_summary,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            }
        }, status=status.HTTP_200_OK)


    # GET /admin/reports/wallet-summary
    @action(detail=False, methods=['get'], url_path='wallet-summary')
    def wallet_summary(self, request):

        total_reimbursed = Transaction.objects.filter(type='credit').aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_withdrawn = Transaction.objects.filter(type='debit').aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_pending = WithdrawalRequest.objects.filter(status='pending').aggregate(
            total=Sum('amount')
        )['total'] or 0

        return Response({
            "total_reimbursed": total_reimbursed,
            "total_withdrawn": total_withdrawn,
            "total_pending": total_pending
        }, status=status.HTTP_200_OK)


    # GET /admin/reports/auto-approval-stats
    @action(detail=False, methods=['get'], url_path='auto-approval-stats')
    def auto_approval_stats(self, request):

        total_auto_approved = Expense.objects.filter(status='auto_approved').count()
        pending_auto_approval = Expense.objects.filter(status='pending').count()
        manually_actioned = Expense.objects.filter(status__in=['approved', 'rejected']).count()

        return Response({
            "total_auto_approved": total_auto_approved,
            "pending_auto_approval": pending_auto_approval,
            "manually_actioned" : manually_actioned
        }, status=status.HTTP_200_OK)