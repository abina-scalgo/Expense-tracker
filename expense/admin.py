from django.contrib import admin
from .models import ExpenseCategory, Expense

# Register your models here.
admin.site.register(ExpenseCategory)
# admin.site.register(Expense)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'category', 'status')
