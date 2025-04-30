import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

# Server environment
SERVER_TYPE = os.getenv('SERVER_TYPE', 'LOCAL').upper()
SERVER_NAME = os.getenv('SERVER_NAME', 'LOCAL')

# Debug
DEBUG = SERVER_TYPE == 'LOCAL'

# Frontend info
FRONTEND_IP = os.getenv("FRONTEND_IP", "http://localhost")
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "5173")

# Allowed hosts
if SERVER_TYPE == 'LOCAL':
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = ['pcb-design-5nqf.onrender.com', 'localhost', 'inchawsweb0001']

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'import_export',
    'drf_yasg',
    'corsheaders',
    'right_to_draw',
    'authentication',
    'masters',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.current_user_middleware.CurrentUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pcb_design.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'pcb_design.wsgi.application'

AUTH_USER_MODEL = 'authentication.CustomUser'

ODBC_DRIVER = 'ODBC Driver 17 for SQL Server' if SERVER_TYPE == 'LOCAL' else 'ODBC Driver 13 for SQL Server'

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'OPTIONS': {
            'driver': ODBC_DRIVER,
            'autocommit': True,
            'extra_params': 'DataTypeCompatibility=80;MARS Connection=True;',
            'use_legacy_date_fields': True,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'authentication.custom_authentication.CustomJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'authentication.custom_permissions.IsAuthorized',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=150),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
APPEND_SLASH = False

# CORS
if SERVER_TYPE == 'LOCAL':
    CORS_ALLOWED_ORIGINS = [
        'http://127.0.0.1:5173',
        'http://localhost:5173',
        f"{FRONTEND_IP}:{FRONTEND_PORT}",
    ]
else:
    cors_origin = f"{FRONTEND_IP}:{FRONTEND_PORT}"
    CORS_ALLOWED_ORIGINS = [cors_origin]
    if SERVER_NAME == 'DEV':
        CORS_ALLOWED_ORIGINS.append('http://localhost:5173')

CORS_ALLOW_CREDENTIALS = True
