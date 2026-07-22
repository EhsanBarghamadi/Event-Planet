from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # OpenAPI / Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Admin Panel
    path('admin/', admin.site.urls),

    # Versioned App Endpoints
    path('api/<str:version>/user/', include('user.urls')),
    path('api/<str:version>/', include('event.urls')),
    path('api/<str:version>/', include('attribute.urls')),
    path('api/<str:version>/', include('relation.urls')),
]