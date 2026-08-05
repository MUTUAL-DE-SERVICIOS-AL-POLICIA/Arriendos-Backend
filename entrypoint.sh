#!/bin/bash
set -e

echo "========================================="
echo "  ARRIENDOS BACKEND"
echo "  Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Entorno: ${ENVIRONMENT:-development}"
echo "========================================="

# Esperar a que la base de datos este lista (max 60 segundos)
echo "Verificando conexion a PostgreSQL..."
python -c "
import time, sys
try:
    import psycopg2
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary', '-q'])
    import psycopg2

host = '${DB_HOST:-127.0.0.1}'
port = '${DB_PORT:-5432}'
dbname = '${DB_NAME:-bd_arriendos}'
user = '${DB_USER:-postgres}'
password = '${DB_PASSWORD:-123456}'

for i in range(30):
    try:
        conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        conn.close()
        print(f'  BD conectada: {host}:{port}/{dbname}')
        sys.exit(0)
    except psycopg2.OperationalError as e:
        print(f'  Intento {i+1}/30 - BD no disponible, esperando 2s...')
        time.sleep(2)

print(f'  ERROR: No se pudo conectar a {host}:{port}/{dbname}')
sys.exit(1)
"

# Aplicar migraciones
echo "Aplicando migraciones..."
python manage.py migrate --noinput
echo "  Migraciones aplicadas correctamente."

# Precargar imagenes de ambientes
echo "Precargando imagenes de ambientes..."
python manage.py seed_images

# Iniciar servidor segun entorno
echo "========================================="
echo "  Iniciando servidor..."
echo "========================================="
if [ "$ENVIRONMENT" = "production" ]; then
    echo "  Modo: PRODUCCION (Gunicorn)"
    exec gunicorn -c gunicorn_config.py Arriendos_Backend.wsgi:application
else
    echo "  Modo: DESARROLLO (runserver)"
    exec python manage.py runserver 0.0.0.0:9005
fi
