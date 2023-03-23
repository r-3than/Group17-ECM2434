"""
Django settings for projectGreen project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT = os.path.join(BASE_DIR, '').replace('\\', '/')
MEDIA_URL = '/uploads/'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*f-8r*xtx6mljgv8pdcp^^)z&y&80r1p_iyf!y_lf=*0600$ca'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file_app': {
            'class': 'logging.FileHandler',
            'filename': 'projectGreen.log',
            'formatter': 'simple',
        },
        'file_game_master': {
            'class': 'logging.FileHandler',
            'filename': 'gameMaster.log',
            'formatter': 'simple',
        },
        'file_global': {
            'class': 'logging.FileHandler',
            'filename': 'django_debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'projectGreen.models': {
            'level': 'INFO',
            'handlers': ['file_app'],
        },
        'gameMaster': {
            'level;': 'INFO',
            'handlers': ['file_game_master'],
        },
        'django': {
            'level': 'DEBUG',
            'handlers': ['file_global'],
            'propogate': True,
        },
    },
    'formatters': {
        'simple': {
            'format': '{asctime} [{levelname}]: {message}',
            'style': '{',
        },
        'verbose': {
            'format': '{asctime} [{name} {levelname} IN {module}]: {message}',
            'style': '{',
        },
    },
}

broadcastURL = "http://localhost:8000" # change this url to the hosting url and make sure below
ALLOWED_HOSTS = ["projectgreen.grayitsolutions.com","localhost"]
CSRF_TRUSTED_ORIGINS = ['https://projectgreen.grayitsolutions.com',"http://localhost:8000"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'projectGreen'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'projectGreen.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates/"],
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

WSGI_APPLICATION = 'projectGreen.wsgi.application'

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'djangotestemail31@gmail.com'
EMAIL_HOST_PASSWORD = 'nrsrhztfmmwyqzey'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  BASE_DIR / 'db.sqlite3'
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


MICROSOFT = {
    "app_id": "24bdff02-06db-48b9-b65a-da869ccd651d",
    "app_secret": "mXr8Q~b8BO9E9gI~Lv38QCFcO2G45Rc27nv6AajQ",
    "redirect": broadcastURL+"/microsoft_authentication/callback",
    "scopes": ["user.read"],
    "authority": "https://login.microsoftonline.com/common",  # or using tenant "https://login.microsoftonline.com/{tenant}",
    "valid_email_domains": ["exeter.ac.uk"],
    "logout_uri": broadcastURL
}

LOGIN_URL = "/microsoft_authentication/login"
LOGIN_REDIRECT_URL = "/"  # optional and can be changed to any other url


# True: creates new Django User after valid microsoft authentication.
# False: it will only allow those users which are already created in Django User model and
# will validate the email using Microsoft.
MICROSOFT_CREATE_NEW_DJANGO_USER = True  # Optional, default value is True


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1

PROFANITY_FILTER_SOURCE_URL = 'https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/badwordslist/badwords.txt'