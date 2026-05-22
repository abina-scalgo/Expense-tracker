from rest_framework import serializers
from .models import ExpenseCategory, Expense, ExpenseReceipt
import os
from django.db import transaction
from wallets.models import Wallet

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'

    def validate_name(self, value):
        # Check uniqueness only among active categories
        qs = ExpenseCategory.objects.filter(name__iexact=value, is_active=True)

        # Exclude current instance when updating
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError("expense category with this name already exists.")
        
        return value

class ExpenseReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseReceipt
        fields = ['id', 'file', 'file_name', 'file_type', 'file_size_kb', 'uploaded_at']

class ExpenseSerializer(serializers.ModelSerializer):
    receipts = ExpenseReceiptSerializer(many=True, read_only=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Expense
        fields = [
            'id', 'category', 'amount', 'note', 'status', 
            'expense_date', 'receipts', 'uploaded_files', 'created_at'
        ]
        read_only_fields = ['status', 'id', 'created_at']

    # File Validation
    def validate_uploaded_files(self, files):

        allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf']
        max_size_mb = 5

        for file_obj in files:
            extension = (
                os.path.splitext(file_obj.name)[1].lower().replace('.', '')
            )

            if extension not in allowed_extensions:
                raise serializers.ValidationError(f'{extension} files are not allowed. ')

            if file_obj.size > max_size_mb *1024 *1024:
                raise serializers.ValidationError(f'File size exceeds 5MB.')
            
        return files

    # Create Expense
    def create(self, validated_data):

        uploaded_files = validated_data.pop('uploaded_files', [])

        with transaction.atomic():
            expense = Expense.objects.create(**validated_data)

            #Update Wallet
            wallet, created = (
                Wallet.objects.select_for_update().get_or_create(
                    user=expense.user
                )
            )
            wallet.pending_amount += expense.amount
            wallet.save()

            for file_obj in uploaded_files:
                original_name = file_obj.name

                extension = (
                    os.path.splitext(original_name)[1].lower().replace('.', '')
                )

                size_kb = int(file_obj.size / 1024)

                ExpenseReceipt.objects.create(
                    expense=expense,
                    file=file_obj,
                    file_name=original_name,
                    file_type=extension,
                    file_size_kb=size_kb
                )

        return expense