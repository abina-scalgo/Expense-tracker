from rest_framework import serializers
from .models import ExpenseCategory, Expense, ExpenseReceipt
import os

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

    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_files', [])
        expense = Expense.objects.create(**validated_data)
        
        for file_obj in uploaded_files:
            # Extract metadata for the ExpenseReceipt model
            original_name = file_obj.name
            extension = os.path.splitext(original_name)[1].lower().replace('.', '')
            size_kb = int(file_obj.size / 1024)

            ExpenseReceipt.objects.create(
                expense=expense,
                file=file_obj,
                file_name=original_name,
                file_type=extension,
                file_size_kb=size_kb
            )
        return expense
