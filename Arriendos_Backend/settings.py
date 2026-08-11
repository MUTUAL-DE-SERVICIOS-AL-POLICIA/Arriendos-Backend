"""
Django settings — ARRIENDOS BACKEND
====================================

Este archivo sirve para TODOS los entornos (local, pruebas, produccion).
La configuracion se controla mediante VARIABLES DE ENTORNO.

ENTORNOS:
  - LOCAL:      DB local, LDAP desactivado, DEBUG=True
  - PRUEBAS:    DB remota, LDAP activo, DEBUG=True
  - PRODUCCION: DB remota, LDAP activo, DEBUG=False

COMO FUNCIONA:
  1. Crea un archivo .env en la raiz del proyecto (o usa variables de entorno del contenedor)
  2. os.environ.get() lee esas variables con un valor por defecto
  3. Si no existe la variable, usa el valor por defecto (local)

VARIABLES DE ENTORNO REQUERIDAS (ver .env.example):
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
  SECRET_KEY, DEBUG, ALLOWED_HOSTS, CORS_ORIGINS
  LDAP_STATUS, LDAP_SERVER, LDAP_USER, LDAP_PASSWORD
  ENVIRONMENT, GUNICORN_WORKERS, GUNICORN_THREADS, GUNICORN_TIMEOUT
"""

from pathlib import Path
from datetime import timedelta
import os
import sys

# ============================================================
# 1. PATHS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = os.path.join(str(BASE_DIR), 'Arriendos-Backend') if os.path.exists(
    os.path.join(str(BASE_DIR), 'Arriendos-Backend')) else str(BASE_DIR)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# ============================================================
# 2. SECURITY
# ============================================================
# IMPORTANTE: Genera una clave unica por entorno:
#   python -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-desarrollo-local-cambiar-en-produccion')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

# Hosts permitidos (separados por coma en la variable de entorno)
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')]

# ============================================================
# 3. APPS
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    'threadlocals',
    'login',
    'rooms',
    'customers',
    'plans',
    'users',
    'products',
    'requirements',
    'leases',
    'financials',
    'roles',
    'records',
]

# ============================================================
# 4. MIDDLEWARE
# ============================================================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'threadlocals.middleware.ThreadLocalMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'records.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'Arriendos_Backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Arriendos_Backend.wsgi.application'

# ============================================================
# 5. DATABASE
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'bd_arriendos'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# ============================================================
# 6. AUTH
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================================
# 7. INTERNATIONALIZATION
# ============================================================
LANGUAGE_CODE = 'es-bo'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ============================================================
# 8. STATIC / MEDIA FILES
# ============================================================
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# 9. CORS
# ============================================================
# URLs del frontend permitidas (separadas por coma)
_cors_raw = os.environ.get('CORS_ORIGINS', 'http://localhost:9006')
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_raw.split(',') if o.strip()]
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Solo en desarrollo

# ============================================================
# 10. REST FRAMEWORK
# ============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# ============================================================
# 11. JWT
# ============================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# ============================================================
# 12. LDAP
# ============================================================
LDAP_STATUS = os.environ.get('LDAP_STATUS', 'False').lower() in ('true', '1', 'yes')
LDAP_SERVER = os.environ.get('LDAP_SERVER', '')
LDAP_USER = os.environ.get('LDAP_USER', '')
LDAP_PASSWORD = os.environ.get('LDAP_PASSWORD', '')
LDAP_USER_DN = os.environ.get('LDAP_USER_DN', '')
LDAP_BASE = os.environ.get('LDAP_BASE', '')
LDAP_FILTER = os.environ.get('LDAP_FILTER', '(objectClass=*)')
ATTRIBUTES = ['uid', 'givenName', 'sn', 'mail']

# ============================================================
# 13. SWAGGER
# ============================================================
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {},
}

# ============================================================
# 14. LOGGING — Archivos en carpetas por dia
# ============================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'access_file': {
            'class': 'records.handlers.DailyFolderHandler',
            'base_dir': os.path.join(BASE_DIR, 'logs'),
            'filename': 'access.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'records.handlers.DailyFolderHandler',
            'base_dir': os.path.join(BASE_DIR, 'logs'),
            'filename': 'errors.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'class': 'records.handlers.DailyFolderHandler',
            'base_dir': os.path.join(BASE_DIR, 'logs'),
            'filename': 'security.log',
            'formatter': 'verbose',
        },
        'business_file': {
            'class': 'records.handlers.DailyFolderHandler',
            'base_dir': os.path.join(BASE_DIR, 'logs'),
            'filename': 'business.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': [],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.server': {
            'handlers': [],
            'level': 'INFO',
            'propagate': False,
        },
        'records.access': {
            'handlers': ['access_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'records.error': {
            'handlers': ['error_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'business': {
            'handlers': ['business_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
