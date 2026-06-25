from django.urls import path
from .views import (
    UserRegisterView,
    UserSessionLoginView,
    MyTokenObtainPairView,
    UserSessionLogoutView,
    LogoutView,
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserSessionLoginView.as_view(), name='login'),
    path('logout/', UserSessionLogoutView.as_view(), name='logout'),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth_logout'),
]

