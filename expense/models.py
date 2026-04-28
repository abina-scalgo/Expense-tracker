from django.db import models
import uuid

# Create your models here.

class ExpenseCategory(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'expense_categories'
        ordering = ['name']
        verbose_name_plural = 'Expense Categories'

    def __str__(self):
        return self.name