from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Settings Django-Debug-Toolbar

INSTALLED_APPS += [
    # Third Party
    "debug_toolbar",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

MIDDLEWARE.insert(
    0,
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)