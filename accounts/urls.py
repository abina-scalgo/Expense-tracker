from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, 
    CustomTokenObtainPairView, 
    LogoutView, 
    BankDetailsViewSet
)
from rest_framework_simplejwt.views import TokenRefreshView

# Initialize the router
router = DefaultRouter()
router.register(r'bank-details', BankDetailsViewSet, basename='bank-detail')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'), 
    # Allows the app to get a new access token without making the user type their password again.
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Include the router URLs
    path('', include(router.urls)),
]
