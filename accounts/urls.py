from django.urls import path
from .views import UserRegistrationView, CustomTokenObtainPairView, UserListView, UserDetailUpdateDeleteView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('admin/users/', UserListView.as_view(), name='list-users'),
    path('admin/users/<uuid:id>/', UserDetailUpdateDeleteView.as_view(), name='user-admin-detail'),
    # Essential for mobile: allows the app to get a new access token 
    # without making the user type their password again.
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
