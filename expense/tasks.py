import logging
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from expense.models import Expense
from core.models import CeleryTaskLogs
from wallets.models import (
    Wallet,
    Transaction
)
from notifications.models import Notification

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_auto_approvals(self):
    now = timezone.now()

    task_log = CeleryTaskLogs.objects.create(
        task_name="expense.tasks.process_auto_approvals",
        task_id=self.request.id,
        status="started",
        executed_at=now
    )

    try:
        expenses = Expense.objects.filter(
            status=Expense.Status.PENDING,
            auto_approve_at__lte=now
        ).iterator(chunk_size=100)
        processed = 0

        for expense in expenses:
            try:
                with transaction.atomic():

                    expense = (
                        Expense.objects.select_for_update().get(id=expense.id)
                    )

                    # Prevent duplicate processing
                    if expense.status != Expense.Status.PENDING:
                        continue

                    # Auto Approve
                    expense.status = (
                        Expense.Status.AUTO_APPROVED
                    )
                    expense.actioned_by = None
                    expense.actioned_at = now
                    expense.save()

                    # Wallet Update
                    wallet, created = (
                        Wallet.objects.select_for_update().get_or_create(user=expense.user)
                    )

                    if wallet.pending_amount >= expense.amount:
                        wallet.pending_amount -= (
                            expense.amount
                        )
                    wallet.available_balance += (
                        expense.amount
                    )
                    wallet.save()

                    # Transaction
                    Transaction.objects.create(
                        wallet=wallet,
                        expense=expense,
                        amount = expense.amount,
                        type="credit",
                        description=(
                            "Expense auto approved "
                            "by time threshold"
                        )
                    )

                    # Notification
                    Notification.objects.create(
                        user=expense.user,
                        title="Expense Auto Approved",
                        message=(
                            f"Your expense of "
                            f"₹{expense.amount} "
                            f"was auto approved. "
                        ),
                        type="expense_auto_approved"
                    )

                    processed += 1

            except Exception as row_error:

                logger.error(
                    f"Expense {expense.id} failed: "
                    f"{str(row_error)}"
                )
        task_log.status = "success"
        task_log.result = (
            f"Processed {processed} expenses"
        )
        task_log.completed_at = timezone.now()
        task_log.save()
        return task_log.result
    
    except Exception as e:
        task_log.status = "failed"
        task_log.result = str(e)
        task_log.completed_at = timezone.now()
        task_log.save()
        raise