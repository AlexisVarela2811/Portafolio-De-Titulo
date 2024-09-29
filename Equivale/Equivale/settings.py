"""
Django settings for Equivale project.

Generated by 'django-admin startproject' using Django 3.2.22.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-jpvg81y-u@8x*!$68f_$in5aif9vjrj^n)yg%7*9@qqc-rx#gf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #Aplicaciones instaladas
    'cuentas',
    'productos',
    #RestFramwork
    'rest_framework',
    'rest_framework.authtoken',
    #OAuth
    'social_django',
]

AUTH_USER_MODEL = 'cuentas.Usuario'

REST_FRAMEWORK = {
    # Clases de autenticación que se utilizarán para autenticar a los usuarios basado en tokens.
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    # Clases de permisos que se aplicarán a las vistas de la API.
    # Aquí, se especifica que solo los usuarios autenticados podrán acceder a las vistas.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #OAuth
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'Equivale.urls'

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
                #OAuth
                'social_django.context_processors.backends',
            ],
        },
    },
]

WSGI_APPLICATION = 'Equivale.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

#Conexion a base de datos ORACLE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'localhost:1521/xe',
        'USER': 'c##equivale',
        'PASSWORD': 'equivalebd',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static'),
]

#Imagenes
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#OAuth APP settings custom
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',

    #OAuth GITHUB
    'social_core.backends.github.GithubOAuth2',
    #OAuth Google
    'social_core.backends.google.GoogleOAuth2',
]

LOGIN_URL = '/cuentas/login/'
LOGIN_REDIRECT_URL = '/cuentas/perfil'  
LOGOUT_URL = '/cuentas/logout/'
LOGOUT_REDIRECT_URL = '/cuentas/login/'  


#OAuth GITHUB
SOCIAL_AUTH_GITHUB_KEY = ''
SOCIAL_AUTH_GITHUB_SECRET = ''

#OAuth Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''

#Paypal
PAYPAL_CLIENT_ID = ''
PAYPAL_CLIENT_SECRET = ''
PAYPAL_MODE = 'sandbox'   #live para despliegue real 
SITE_URL = 'http://127.0.0.1:8000'

SOCIAL_AUTH_PIPELINE = [
    'social_core.pipeline.social_auth.social_details',  
    'social_core.pipeline.social_auth.social_uid',  
    'social_core.pipeline.social_auth.auth_allowed',  
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',  
    'social_core.pipeline.social_auth.associate_by_email',  
    'social_core.pipeline.social_auth.associate_user',  
    'social_core.pipeline.social_auth.load_extra_data',  
    'social_core.pipeline.user.user_details',  
    'cuentas.pipelines.save_user_from_oauth',
]

SOCIAL_AUTH_GITHUB_SCOPE = ['user:email']