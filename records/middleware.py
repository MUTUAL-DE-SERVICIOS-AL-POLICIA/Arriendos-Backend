"""
Middleware de logging para registros HTTP.

Registra todas las peticiones HTTP entrantes en los archivos de log
correspondientes (access.log, errors.log).

Autor: Dilan Torrez
Fecha: 2026
"""

import logging
import time

access_logger = logging.getLogger('django.request')
error_logger = logging.getLogger('django.request')


class RequestLoggingMiddleware:
    """
    Middleware que registra cada peticion HTTP en los archivos de log.

    Registra:
    - Metodo HTTP (GET, POST, PUT, etc.)
    - Ruta solicitada
    - Codigo de respuesta
    - Tiempo de respuesta
    - IP del cliente
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        status_code = response.status_code
        method = request.method
        path = request.path
        ip = self.get_client_ip(request)
        user = request.user.username if request.user.is_authenticated else 'anonymous'

        log_message = f"{method} {path} {status_code} {duration:.3f}s user={user} ip={ip}"

        if status_code >= 500:
            error_logger.error(log_message)
        elif status_code >= 400:
            error_logger.warning(log_message)
        else:
            access_logger.info(log_message)

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
