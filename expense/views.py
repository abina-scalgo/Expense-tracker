from django.shortcuts import render
from .models import ExpenseCategory

from rest_framework.viewsets import ModelViewSet
from .models import ExpenseCategory
from .serializers import ExpenseCategorySerializer
from .permissions import IsAdminRoleOrReadOnly
from rest_framework.permissions import IsAuthenticated


# Create your views here.

#Add the expense category
class ExpenseCategoryViewSet(ModelViewSet):
    # queryset = ExpenseCategory.objects.all().order_by('-created_at')
    queryset = ExpenseCategory.objects.filter(is_active=True)
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminRoleOrReadOnly]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        return "deleted successfully"