from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # UserRegistrationView, 
    CustomTokenObtainPairView, 
    LogoutView, 
    ChangePasswordView,
    BankDetailsViewSet,
    UserAdminViewSet
)
from rest_framework_simplejwt.views import TokenRefreshView

# Initialize the router
router = DefaultRouter()
router.register(r'admin/users', UserAdminViewSet, basename='admin-users')
router.register(r'bank-details', BankDetailsViewSet, basename='bank-detail')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'), 
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    # Allows the app to get a new access token without making the user type their password again.
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Include the router URLs
    path('', include(router.urls)),
]
