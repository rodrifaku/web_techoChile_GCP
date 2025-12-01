"""
Middleware personalizado para depuración de CSRF en Cloud Run
"""
import logging

logger = logging.getLogger(__name__)


class CsrfDebugMiddleware:
    """
    Middleware para loguear información detallada cuando falla la verificación CSRF
    Útil para depurar problemas en Cloud Run
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Captura excepciones CSRF y loguea información de depuración
        """
        if exception.__class__.__name__ == 'PermissionDenied':
            # Probable error CSRF
            logger.warning(
                f"[CSRF DEBUG] Posible error CSRF en {request.path}\n"
                f"  Method: {request.method}\n"
                f"  Origin: {request.META.get('HTTP_ORIGIN', 'N/A')}\n"
                f"  Referer: {request.META.get('HTTP_REFERER', 'N/A')}\n"
                f"  Host: {request.META.get('HTTP_HOST', 'N/A')}\n"
                f"  X-Forwarded-Proto: {request.META.get('HTTP_X_FORWARDED_PROTO', 'N/A')}\n"
                f"  X-Forwarded-For: {request.META.get('HTTP_X_FORWARDED_FOR', 'N/A')}\n"
                f"  User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')[:100]}\n"
                f"  CSRF Cookie: {'presente' if request.META.get('CSRF_COOKIE') else 'ausente'}\n"
                f"  Session Key: {'presente' if request.session.session_key else 'ausente'}"
            )
        return None


class CsrfCookieEnforcerMiddleware:
    """
    Middleware para asegurar que todas las respuestas establezcan la cookie CSRF
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Forzar la creación del token CSRF
        from django.middleware.csrf import get_token
        get_token(request)
        
        response = self.get_response(request)
        return response
