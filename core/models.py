import uuid
from django.conf import settings
from django.db import models

# Create your models here.

class SystemSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='updated_settings'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Setting'

    def __str__(self):
        return self.key
    

class CeleryTaskLogs(models.Model):
    STATUS_CHOICES = (
        ('started', 'Started'),
        ('success', 'Success'),
        ('failed', 'Failed')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_name = models.CharField(max_length=100)
    task_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    expense = models.ForeignKey(
        'expense.Expense',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='celery_logs'
    )
    result = models.TextField(blank=True, null=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'celery_task_logs'
        verbose_name = 'Celery Task Log'
        ordering = ['-executed_at']

    def __str__(self):
        return f"{self.task_name} - {self.task_id} ({self.status})"