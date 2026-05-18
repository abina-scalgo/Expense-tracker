from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from django.utils import timezone
from .models import Notification

Expense = apps.get_model('expense', 'Expense')

@receiver(post_save, sender=Expense)
def monitor_expense_events(sender, instance, created, **kwargs):
    """
    Handles: new_expense, expense_approved, expense_rejected, expense_auto_approved
    """
    # Action: New Expense Submitted
    if created:
        Notification.objects.create(
            user=instance.user,
            title="New Expense Submitted",
            message=f"Your expense claim of Rs.{instance.amount} has been successfully logged for review.",
            type="new_expense"
        )
        return

    # Track State Changes on Expense Updates
    if instance.status == 'approved':
        # Guard clause prevents duplicate entries if model saves multiple times
        if not Notification.objects.filter(user=instance.user, type="expense_approved", message__contains=str(instance.id)).exists():
            Notification.objects.create(
                user=instance.user,
                title="Expense Approved",
                message=f"Your expense claim of Rs.{instance.amount} (ID: {instance.id}) has been approved.",
                type="expense_approved"
            )
            
    elif instance.status == 'rejected':
        if not Notification.objects.filter(user=instance.user, type="expense_rejected", message__contains=str(instance.id)).exists():
            Notification.objects.create(
                user=instance.user,
                title="Expense Rejected",
                message=f"Your expense claim of Rs.{instance.amount} (ID: {instance.id}) was rejected.",
                type="expense_rejected"
            )
            
    elif instance.status == 'auto_approved':
        if not Notification.objects.filter(user=instance.user, type="expense_auto_approved", message__contains=str(instance.id)).exists():
            Notification.objects.create(
                user=instance.user,
                title="Expense Auto Approved",
                message=f"System rules have auto-approved your expense claim of Rs.{instance.amount} (ID: {instance.id}).",
                type="expense_auto_approved"
            )
