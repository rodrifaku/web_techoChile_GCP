"""
Vista de diagnóstico CSRF para Cloud Run
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
import os


@csrf_exempt
@require_http_methods(["GET"])
def csrf_diagnostic(request):
    """
    Endpoint de diagnóstico para verificar configuración CSRF
    Solo disponible en DEBUG mode o con token especial
    """
    from django.conf import settings
    
    # Verificar autorización
    diagnostic_token = request.GET.get('token', '')
    is_authorized = (
        settings.DEBUG or 
        diagnostic_token == os.getenv('DIAGNOSTIC_TOKEN', 'change-me-in-production')
    )
    
    if not is_authorized:
        return JsonResponse({
            'error': 'Unauthorized',
            'message': 'This endpoint requires DEBUG=True or valid diagnostic token'
        }, status=403)
    
    # Recopilar información de diagnóstico
    csrf_token = get_token(request)
    
    diagnostic_info = {
        'csrf_configuration': {
            'CSRF_COOKIE_SECURE': getattr(settings, 'CSRF_COOKIE_SECURE', None),
            'CSRF_COOKIE_HTTPONLY': getattr(settings, 'CSRF_COOKIE_HTTPONLY', None),
            'CSRF_COOKIE_SAMESITE': getattr(settings, 'CSRF_COOKIE_SAMESITE', None),
            'CSRF_COOKIE_DOMAIN': getattr(settings, 'CSRF_COOKIE_DOMAIN', None),
            'CSRF_TRUSTED_ORIGINS': getattr(settings, 'CSRF_TRUSTED_ORIGINS', []),
            'CSRF_USE_SESSIONS': getattr(settings, 'CSRF_USE_SESSIONS', None),
        },
        'session_configuration': {
            'SESSION_COOKIE_SECURE': getattr(settings, 'SESSION_COOKIE_SECURE', None),
            'SESSION_COOKIE_HTTPONLY': getattr(settings, 'SESSION_COOKIE_HTTPONLY', None),
            'SESSION_COOKIE_SAMESITE': getattr(settings, 'SESSION_COOKIE_SAMESITE', None),
            'SESSION_COOKIE_DOMAIN': getattr(settings, 'SESSION_COOKIE_DOMAIN', None),
            'SESSION_ENGINE': getattr(settings, 'SESSION_ENGINE', None),
        },
        'request_info': {
            'method': request.method,
            'path': request.path,
            'host': request.get_host(),
            'scheme': request.scheme,
            'is_secure': request.is_secure(),
        },
        'headers': {
            'Origin': request.META.get('HTTP_ORIGIN', 'N/A'),
            'Referer': request.META.get('HTTP_REFERER', 'N/A'),
            'Host': request.META.get('HTTP_HOST', 'N/A'),
            'X-Forwarded-Proto': request.META.get('HTTP_X_FORWARDED_PROTO', 'N/A'),
            'X-Forwarded-For': request.META.get('HTTP_X_FORWARDED_FOR', 'N/A'),
            'User-Agent': request.META.get('HTTP_USER_AGENT', 'N/A')[:100],
        },
        'cookies': {
            'csrftoken': request.COOKIES.get('csrftoken', 'N/A'),
            'sessionid': 'presente' if request.COOKIES.get('sessionid') else 'ausente',
        },
        'csrf_token_generated': csrf_token[:10] + '...' if csrf_token else 'N/A',
        'session': {
            'session_key': 'presente' if request.session.session_key else 'ausente',
            'is_empty': request.session.is_empty(),
        },
        'environment': {
            'DEBUG': settings.DEBUG,
            'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
            'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', None),
            'SECURE_PROXY_SSL_HEADER': getattr(settings, 'SECURE_PROXY_SSL_HEADER', None),
        }
    }
    
    return JsonResponse({
        'status': 'ok',
        'message': 'CSRF Diagnostic Information',
        'data': diagnostic_info
    }, json_dumps_params={'indent': 2})
