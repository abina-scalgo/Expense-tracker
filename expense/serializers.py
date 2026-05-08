from rest_framework import serializers
from .models import ExpenseCategory

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