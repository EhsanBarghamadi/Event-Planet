from .base import *
from decouple import config, Csv

SECRET_KEY = config('SECRET_KEY', default='default_secret_key')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'user.CustomUser'

INSTALLED_APPS += [
    #Third Party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist', 
    'django_filters',
    'markdown', 
    'drf_spectacular',
    #Local Apps
    'core',
    'user',
    'event',
    'attribute',
    'relation'
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'ALLOWED_VERSIONS': ['v1', 'v2'],
    'DEFAULT_VERSION': 'v1',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Event Planet API',
    'DESCRIPTION': 'Event Planet description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}