
import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de seguridad - todas las variables sensibles deben estar en .env
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=False, cast=bool)
# Permitir dominios dinámicos de Cloud Run y túneles Cloudflare durante diagnóstico.
# En producción se recomienda restringir más específicamente.
ALLOWED_HOSTS = [
    
    ".dockerdev",
    "127.0.0.1",
    "localhost",
    "34.13.127.157",  # IP del Load Balancer
    ".run.app",       # cualquier subdominio de run.app
    ".trycloudflare.com",  # túneles dev
    ".southamerica-west1.run.app",
    ".southamerica-east1.run.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.run.app",
    "https://*.trycloudflare.com",
    "http://34.13.127.157",
    "https://34.13.127.157",
    "https://*.southamerica-west1.run.app",
    "https://*.southamerica-east1.run.app",
]

# Configuración de seguridad para HTTPS en producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    # Header que indica protocolo cuando estamos detrás de proxy (Cloud Run)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Durante diagnóstico temporal desactivamos redirección forzada para evitar bucles
SECURE_SSL_REDIRECT = False

# Configuración de CSRF y Sesiones para Cloud Run
# CSRF_COOKIE_HTTPONLY debe ser False para que JavaScript pueda leer el token
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'  # 'Lax' permite peticiones desde el mismo sitio
CSRF_USE_SESSIONS = False  # Usar cookie independiente para CSRF
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# Configuración de sesiones
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = False
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Usar base de datos para sesiones

# Permitir cookies en subdominios de run.app
if not DEBUG:
    SESSION_COOKIE_DOMAIN = None  # Usar dominio actual
    CSRF_COOKIE_DOMAIN = None

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
    'core.middleware_csrf.CsrfCookieEnforcerMiddleware',  # Forzar cookie CSRF
    'django.middleware.csrf.CsrfViewMiddleware',
    'core.middleware_csrf.CsrfDebugMiddleware',  # Debug CSRF errors
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

# DEBUG: Verificar credenciales de DB
db_password = config('DB_PASSWORD', default='')
db_user = config('DB_USER', default='django_user')
print(f"[DEBUG] DB_USER: {db_user}, DB_PASSWORD length: {len(db_password) if db_password else 0}")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='django_db'),
        'USER': db_user,
        'PASSWORD': db_password,  # Sin valor por defecto inseguro
        'HOST': config('DB_HOST', default='127.0.0.1'),  # Default: localhost para commits
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Fallback de diagnóstico: permitir usar SQLite si se define USE_SQLITE=true en variables de entorno
USE_SQLITE = os.getenv('USE_SQLITE', 'false').lower() == 'true'
if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Validar que las credenciales críticas estén configuradas en producción
# Solo validar si no estamos en build (collectstatic no necesita DB)
import sys
if not DEBUG and 'collectstatic' not in sys.argv and DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
    required_db_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
    missing_vars = [var for var in required_db_vars if not os.getenv(var)]
    if missing_vars:
        # En vez de abortar el arranque, logueamos advertencia para no dejar el servicio en 503.
        print(
            f"[WARN] Variables de entorno DB faltantes: {', '.join(missing_vars)}. "
            "El servicio inicia pero la conexión a Postgres fallará hasta configurarlas."
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
STATICFILES_DIRS = [BASE_DIR / "static"]

# Configuración de WhiteNoise para servir archivos estáticos
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

USE_GCS_MEDIA = os.getenv("USE_GCS_MEDIA", "false").lower() == "true"
GS_MEDIA_BUCKET_NAME = "techo-chile-media-sa-west1"

if USE_GCS_MEDIA:
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    # Intentar tomar el bucket desde variable de entorno, si no, usar constante definida
    GS_DEFAULT_BUCKET_NAME = os.getenv("GS_MEDIA_BUCKET_NAME") or GS_MEDIA_BUCKET_NAME
    if not GS_DEFAULT_BUCKET_NAME:
        # Falla silenciosa: mantenemos MEDIA_URL local para no romper arranque
        # (Evita crash si se olvidó configurar variable en Cloud Run)
        USE_GCS_MEDIA = False
        DEFAULT_FILE_STORAGE = None
        MEDIA_URL = "/media/"
        MEDIA_ROOT = BASE_DIR / "media"
    else:
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
