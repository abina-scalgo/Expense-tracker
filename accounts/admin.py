from django.contrib import admin
from .models import User, UserDetails, BankDetails

# Register your models here.
admin.site.register(User)

@admin.register(UserDetails)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'designation')

@admin.register(BankDetails)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'ifsc_code', 'bank_name', 'account_holder_name', 'is_primary')