from rest_framework import generics, views
from rest_framework import permissions
from rest_framework import status
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from rest_framework import serializers

from .models import CustomUser
from .serializers import UserRegisterSerializer, UserLoginSerializer, MyTokenObtainPairSerializer, EmptyLogoutSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name='RefreshTokenSerializer',
            fields={'refresh': serializers.CharField(help_text="توکن ریفرش برای بلک‌لیست شدن")}
        ),
        responses={
            205: inline_serializer(name='LogoutSuccessResponse', fields={'message': serializers.CharField()}),
            400: inline_serializer(name='LogoutErrorResponse', fields={'error': serializers.CharField()})
        }
    )

    def post(self, request, version, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out."}, 
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer

class UserSessionLoginView(views.APIView):
    @extend_schema(
            request=UserLoginSerializer,
            responses={200: UserLoginSerializer}
        )
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'detail': 'ورود با موفقیت انجام شد.',
                'user': {
                    'phone': user.phone,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            }, status=status.HTTP_200_OK)
        
class UserSessionLogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptyLogoutSerializer

    @extend_schema(
        responses={
            200: inline_serializer(name='SessionLogoutResponse', fields={'detail': serializers.CharField()})
        }
    )
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"detail": "Logged out."}, status=status.HTTP_200_OK)  