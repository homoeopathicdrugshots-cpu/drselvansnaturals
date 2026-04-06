import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================== SECURITY SETTINGS ========================
SECRET_KEY = 'django-insecure-88e419097511f01645229d01a12d1c410fdfc0b3'
DEBUG = False

# DIRECTLY SET ALLOWED HOSTS - NO ENVIRONMENT VARIABLE
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    'drselvansnaturals-3.onrender.com',
]

# ======================== INSTALLED APPS ========================
INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
]

# ======================== MIDDLEWARE ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ======================== URL CONFIGURATION ========================
ROOT_URLCONF = 'drnaturals.urls'

# ======================== TEMPLATES ========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processors.cart_count',
            ],
        },
    },
]

# ======================== DATABASE ========================
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600
    )
}

# ======================== AUTHENTICATION ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ======================== INTERNATIONALIZATION ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ======================== STATIC & MEDIA FILES ========================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ======================== DEFAULT FIELD ========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ======================== CART SETTINGS ========================
CART_SESSION_ID = 'cart'

# ======================== CHECKOUT SETTINGS ========================
FREE_SHIPPING_THRESHOLD = 800
DELIVERY_CHARGE = 75
FORCE_FREE_DELIVERY = True

# ======================== RAZORPAY PAYMENT SETTINGS ========================
RAZORPAY_KEY_ID = 'rzp_live_SY6o5bSYNMMhpC'
RAZORPAY_KEY_SECRET = 'c3KP2OcWjO4thY48aVWle4SR'

# ======================== EMAIL SETTINGS ========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'care@drselvanshomeopathy.com'
EMAIL_HOST_PASSWORD = 'Drselvan@2025'
DEFAULT_FROM_EMAIL = 'Dr Naturals <care@drselvanshomeopathy.com>'
ORDER_ALERT_EMAIL = 'care@drselvanshomeopathy.com'