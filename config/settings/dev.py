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
    #Local Apps
    'core',
    'user',
    'event',
]