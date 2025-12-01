
import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de seguridad - todas las variables sensibles deben estar en .env
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=False, cast=bool)
#ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "34.13.127.157",  # IP del Load Balancer
    "techo-django-47670800654.southamerica-west1.run.app",
    "techo-django-47670800654.southamerica-east1.run.app",
    "carolina-take-consequence-occupation.trycloudflare.com"
    
]

CSRF_TRUSTED_ORIGINS = [
    
    "https://*.trycloudflare.com",   # útil cuando el subdominio rota (DEV)
    "https://techo-django-47670800654.southamerica-west1.run.app",
    "https://techo-django-47670800654.southamerica-east1.run.app",
    "http://34.13.127.157",
    "https://34.13.127.157",
]

# Configuración de seguridad para HTTPS en producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'proyectos',
    'incidencias',
    'reportes',
    'ficha_postventa',
    "django_extensions",
    #'livereload',
    "storages",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'livereload.middleware.LiveReloadScript',
]

ROOT_URLCONF = 'techo_chile.urls'

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
                'core.context_processors.global_stats_context',
                'core.context_processors.permisos_usuario',
            ],
        },
    },
]

WSGI_APPLICATION = 'techo_chile.wsgi.application'

# Configuración de base de datos
# Valores por defecto: localhost (para desarrollo local con DB local)
# Para usar IP externa en local, crea un archivo .env.local con tus credenciales
# El archivo .env.local NO se sube a git (está en .gitignore)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='django_db'),
        'USER': config('DB_USER', default='django_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),  # Sin valor por defecto inseguro
        'HOST': config('DB_HOST', default='127.0.0.1'),  # Default: localhost para commits
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Validar que las credenciales críticas estén configuradas en producción
if not DEBUG:
    required_db_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
    missing_vars = [var for var in required_db_vars if not config(var, default=None)]
    if missing_vars:
        raise ValueError(
            f"Variables de entorno faltantes en producción: {', '.join(missing_vars)}. "
            "Por favor, configura estas variables en tu archivo .env o variables de entorno."
        )


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'proyecto_techo_chile_9650',
#      'USER': 'proyecto_techo_chile_9650_user',
#       'PASSWORD': 'DSvRyHTvF11ei6t4DBC93ysCIuVK984h',
#        'HOST': 'dpg-d3tdnpgdl3ps73ebdu00-a.virginia-postgres.render.com',
#       'PORT': '5432',
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


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

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
USE_GCS_MEDIA = os.getenv("USE_GCS_MEDIA", "false").lower() == "true"
GS_MEDIA_BUCKET_NAME = "techo-chile-media-sa-west1"

if USE_GCS_MEDIA:
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_DEFAULT_BUCKET_NAME = os.getenv("GS_MEDIA_BUCKET_NAME")

    # Si el bucket es público, no necesitas firma en las URLs
    GS_QUERYSTRING_AUTH = False

    MEDIA_URL = f"https://storage.googleapis.com/{GS_DEFAULT_BUCKET_NAME}/"
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.Usuario'

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
# Configuración de email para desarrollo: mostrar correos en consola
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuración de logging para seguridad
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'password_filter': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: 'password' not in str(record.getMessage()).lower() and 'contraseña' not in str(record.getMessage()).lower(),
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['password_filter'],
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'proyectos': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
