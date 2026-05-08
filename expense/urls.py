from rest_framework.routers import DefaultRouter
from .views import ExpenseCategoryViewSet, ExpenseViewSet,AdminExpenseViewSet

router = DefaultRouter()
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expense-category')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'admin/expenses', AdminExpenseViewSet, basename='admin-expense')

urlpatterns = router.urls