from django.urls import path
from .views import UserRegisterView, UserSessionLoginView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserSessionLoginView.as_view(), name='login'),
]

