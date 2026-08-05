"""
Gunicorn Configuration — ARRIENDOS BACKEND
============================================

Workers y threads se configuran via variables de entorno.

REGLA DE WORKERS:
  - 1 CPU core:  2 workers, 2 threads = 4 concurrentes
  - 2 CPU cores: 4 workers, 2 threads = 8 concurrentes
  - 4 CPU cores: 8 workers, 2 threads = 16 concurrentes

VARIABLES DE ENTORNO:
  GUNICORN_WORKERS  - Numero de procesos worker (default: 2)
  GUNICORN_THREADS  - Hilos por worker (default: 2)
  GUNICORN_TIMEOUT  - Timeout en segundos (default: 120)
  GUNICORN_LOG_LEVEL - Nivel de log (default: info)
"""
import os

bind = "0.0.0.0:9005"
workers = int(os.environ.get('GUNICORN_WORKERS', 2))
threads = int(os.environ.get('GUNICORN_THREADS', 2))
module = "Arriendos_Backend.wsgi:application"
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
