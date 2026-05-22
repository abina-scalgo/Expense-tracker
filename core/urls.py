from rest_framework.routers import DefaultRouter
from .views import SystemSettingsViewSet


router = DefaultRouter()
router.register('admin/settings', SystemSettingsViewSet, basename='admin-settings')
urlpatterns = router.urls