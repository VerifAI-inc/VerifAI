from django.urls import path
from .views import SignupView, LoginView, LogoutView, ForgotPasswordView, UserProfileAPIView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    
    # JWT Token Management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("user/profile/", UserProfileAPIView.as_view(), name="user-profile"),
]