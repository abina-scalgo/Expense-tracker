from rest_framework.routers import DefaultRouter
from .views import AdminReportsViewSet

router = DefaultRouter()
router.register(r'admin/reports', AdminReportsViewSet, basename='admin-reports')

urlpatterns = router.urls