# DESPLIEGUE — ARRIENDOS

Guia completa para desplegar Backend y Frontend en los 3 entornos.

---

## TABLA DE CONTENIDOS

1. [Arquitectura](#1-arquitectura)
2. [Requisitos Previos](#2-requisitos-previos)
3. [Despliegue Local (desde cero)](#3-despliegue-local)
4. [Despliegue en Pruebas](#4-despliegue-en-pruebas)
5. [Despliegue en Produccion](#5-despliegue-en-produccion)
6. [Rollback](#6-rollback)
7. [Scripts de Despliegue](#7-scripts-de-despliegue)
8. [Checklist de Despliegue Seguro](#8-checklist-de-despliegue-seguro)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. ARQUITECTURA

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Frontend       │────▶│  Backend        │────▶│  PostgreSQL     │
│  (React/Vite)   │     │  (Django/Gunicorn)│    │  (BD remota)    │
│  Puerto: 83/9006│     │  Puerto: 9005   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Entornos

| Entorno | Servidor | BD | LDAP | DEBUG | Servidor |
|---------|----------|-----|------|-------|----------|
| Local | localhost | Local | Desactivado | True | runserver |
| Pruebas | <IP_SERVIDOR> | <IP_BD>:5438 | Activo | True | runserver |
| Produccion | <IP_PROD> | <IP_PROD>:5432 | Activo | False | Gunicorn |

---

## 2. REQUISITOS PREVIOS

### Para todos los entornos
- [ ] Docker instalado
- [ ] Acceso al repositorio de Git
- [ ] Un archivo `.env` configurado (copiar de `.env.example`)

### Para pruebas y produccion
- [ ] Acceso SSH al servidor
- [ ] Backup de la base de datos (`pg_dump`)
- [ ] Verificar que el backup se puede restaurar

### Generar SECRET_KEY segura
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 3. DESPLIEGUE LOCAL

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/MUTUAL-DE-SERVICIOS-AL-POLICIA/Arriendos-Backend.git
cd Arriendos-Backend
git checkout dev-roles
```

### Paso 2: Configurar variables de entorno
```bash
cp .env.example .env
```

Editar `.env` con valores locales:
```bash
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=bd_arriendos
DB_USER=postgres
DB_PASSWORD=<TU_PASSWORD>

SECRET_KEY=<generar-con-el-comando-de-arriba>
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
ENVIRONMENT=local

LDAP_STATUS=False
```

### Paso 3: Crear la base de datos (si no existe)
```bash
createdb -U postgres bd_arriendos
```

### Paso 4: Levantar Backend con Docker
```bash
docker build -t arriendos:latest .
docker run -d \
  --name arriendos-app \
  --env-file .env \
  -p 9005:9005 \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/logs:/app/logs \
  arriendos:latest
```

### Paso 5: Verificar Backend
```bash
docker logs arriendos-app
# Abrir: http://localhost:9005/swagger/
```

### Paso 6: Cargar datos iniciales (UNA SOLA VEZ)
```bash
docker exec arriendos-app python manage.py loaddata rooms/fixtures/initial_data_property.json
docker exec arriendos-app python manage.py loaddata rooms/fixtures/initial_data_rooms.json
docker exec arriendos-app python manage.py loaddata leases/fixtures/initial_data_state.json
docker exec arriendos-app python manage.py loaddata customers/fixtures/initial_data_customer_type.json
docker exec arriendos-app python manage.py loaddata products/fixtures/initial_data_rate.json
docker exec arriendos-app python manage.py loaddata products/fixtures/initial_data_hour_range.json
docker exec arriendos-app python manage.py loaddata requirements/fixtures/initial_data_requirements.json
```

> **NOTA:** Los fixtures usan PKs hardcodeados. NO ejecutar en una BD con datos existentes.

### Paso 7: Levantar Frontend
```bash
cd ../arriendos-frontend
cp .env.example .env
# Editar .env si es necesario
docker build -t arriendos-frontend:latest .
docker run -d \
  --name arriendos-frontend \
  -p 83:80 \
  arriendos-frontend:latest
```

### Paso 8: Verificar Frontend
```bash
docker logs arriendos-frontend
# Abrir: http://localhost:83/
```

---

## 4. DESPLIEGUE EN PRUEBAS

### Arquitectura del servidor

```
Servidor: <IP_SERVIDOR> (1 CPU, 8GB RAM)
BD:       <IP_BD>:5438 (remota, dedicada)
LDAP:     <IP_LDAP>:3891
Puertos:  Backend 9005, Frontend 83
```

### Paso 1: Conectarse al servidor
```bash
ssh <USUARIO>@<IP_SERVIDOR>
```

### Paso 2: Hacer backup de la BD
```bash
pg_dump -h <IP_BD> -p 5438 -U test -d <NOMBRE_BD> \
  -Fc -f /home/administrador/backups/bd_pruebas_pre_migracion_$(date +%Y%m%d_%H%M).dump
```

### Paso 3: Taggear imagen actual (rollback point)
```bash
# Backend
docker tag arriendos:latest arriendos:backup-$(date +%Y%m%d_%H%M)

# Frontend
docker tag arriendos-frontend:latest arriendos-frontend:backup-$(date +%Y%m%d_%H%M)

# Verificar tags creados
docker images arriendos --format "table {{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"
docker images arriendos-frontend --format "table {{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"
```

### Paso 4: Actualizar codigo Backend
```bash
cd /home/administrador/aplicaciones-dev/Arriendos/Arriendos-Backend
git fetch origin
git checkout dev-roles
git pull origin dev-roles
```

### Paso 5: Crear archivo .env Backend
```bash
cat > .env << 'EOF'
DB_HOST=<IP_BD>
DB_PORT=5438
DB_NAME=<NOMBRE_BD>
DB_USER=test
DB_PASSWORD=<TU_PASSWORD>

SECRET_KEY=<TU_SECRET_KEY>
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,<IP_SERVIDOR>
ENVIRONMENT=development

LDAP_STATUS=True
LDAP_SERVER=ldap://<IP_LDAP>:3891
LDAP_USER=cn=admin,dc=empresa,dc=gob,dc=bo
LDAP_PASSWORD=<TU_PASSWORD_LDAP>

CORS_ORIGINS=http://<IP_SERVIDOR>:83,http://<IP_SERVIDOR>:4300
EOF
```

### Paso 6: Construir y desplegar Backend
```bash
docker build -t arriendos:latest .
docker stop arriendos-app 2>/dev/null || true
docker rm arriendos-app 2>/dev/null || true
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/logs:/app/logs \
  arriendos:latest
```

> **IMPORTANTE:** Los volumenes `media` y `logs` son obligatorios. Sin ellos se pierden los archivos subidos y los logs al recrear el contenedor.

### Paso 7: Verificar Backend
```bash
docker logs arriendos-app
curl -s http://<IP_SERVIDOR>:9005/swagger/
docker exec arriendos-app python manage.py dbshell -c "\dt roles_*"
```

### Paso 8: Actualizar codigo Frontend
```bash
cd /home/administrador/aplicaciones-dev/Arriendos/arriendos-frontend
git fetch origin
git checkout dev-roles
git pull origin dev-roles
```

### Paso 9: Crear archivo .env Frontend
```bash
cat > .env << 'EOF'
VITE_HOST_BACKEND="http://<IP_SERVIDOR>:9005/"
VITE_HOST='<IP_SERVIDOR>'
VITE_PORT='4300'
EOF
```

### Paso 10: Construir y desplegar Frontend
```bash
docker build -t arriendos-frontend:latest .
docker stop arriendos-frontend 2>/dev/null || true
docker rm arriendos-frontend 2>/dev/null || true
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  arriendos-frontend:latest
```

### Paso 11: Verificar Frontend
```bash
docker logs arriendos-frontend
curl -s http://<IP_SERVIDOR>:83/
```

---

## 5. DESPLIEGUE EN PRODUCCION

> **ADVERTENCIA:** Este procedimiento afecta a usuarios reales. Ejecutar solo despues de verificar todo en pruebas.

### Antes de empezar
- [ ] Backup de la BD de produccion verificado
- [ ] Todos los tests pasando en pruebas
- [ ] Login LDAP funcionando en pruebas
- [ ] Frontend funcionando en pruebas
- [ ] Ventana de mantenimiento comunicada (si aplica)
- [ ] Contacto de escalamiento identificado

### Paso 1: Conectarse al servidor
```bash
ssh <usuario_prod>@<IP_PROD>
```

### Paso 2: Hacer backup de la BD
```bash
pg_dump -h <DB_HOST_PROD> -p <DB_PORT_PROD> -U <DB_USER_PROD> -d <DB_NAME_PROD> \
  -Fc -f /home/<user>/backups/bd_prod_pre_migracion_$(date +%Y%m%d_%H%M).dump
```

### Paso 3: Verificar backup
```bash
pg_restore -l /home/<user>/backups/bd_prod_pre_migracion_*.dump > /dev/null && echo "Backup OK"
```

### Paso 4: Taggear imagen actual (rollback point)
```bash
# Backend
docker tag arriendos:latest arriendos:backup-$(date +%Y%m%d_%H%M)

# Frontend
docker tag arriendos-frontend:latest arriendos-frontend:backup-$(date +%Y%m%d_%H%M)

# Verificar
docker images arriendos --format "table {{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"
```

### Paso 5: Actualizar codigo Backend
```bash
cd /home/<user>/aplicaciones/Arriendos/Arriendos-Backend
git fetch origin
git checkout dev-roles
git pull origin dev-roles
```

### Paso 6: Crear archivo .env para produccion
```bash
cat > .env << 'EOF'
DB_HOST=<DB_HOST_PROD>
DB_PORT=<DB_PORT_PROD>
DB_NAME=<DB_NAME_PROD>
DB_USER=<DB_USER_PROD>
DB_PASSWORD=<DB_PASSWORD_PROD>

SECRET_KEY=<SECRET_KEY_PROD>
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,<IP_PROD>
ENVIRONMENT=production

LDAP_STATUS=True
LDAP_SERVER=ldap://<LDAP_SERVER_PROD>
LDAP_USER=<LDAP_USER_PROD>
LDAP_PASSWORD=<LDAP_PASSWORD_PROD>

CORS_ORIGINS=http://<IP_PROD>:83

GUNICORN_WORKERS=<CALCULAR_SEGUN_CPU>
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=120
EOF
```

### Paso 7: Construir y desplegar Backend
```bash
docker build -t arriendos:latest .
docker stop arriendos-app 2>/dev/null || true
docker rm arriendos-app 2>/dev/null || true
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/logs:/app/logs \
  arriendos:latest
```

### Paso 8: Verificar Backend
```bash
docker logs arriendos-app
curl -s http://<IP_PROD>:9005/swagger/
docker exec arriendos-app python manage.py dbshell -c "\dt roles_*"
```

### Paso 9: Actualizar Frontend (si aplica)
```bash
cd /home/<user>/aplicaciones/Arriendos/arriendos-frontend
git fetch origin
git checkout dev-roles
git pull origin dev-roles

# Crear .env
cat > .env << 'EOF'
VITE_HOST_BACKEND="http://<IP_PROD>:9005/"
VITE_HOST='<IP_PROD>'
VITE_PORT='4300'
EOF

# Desplegar
docker build -t arriendos-frontend:latest .
docker stop arriendos-frontend 2>/dev/null || true
docker rm arriendos-frontend 2>/dev/null || true
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  arriendos-frontend:latest
```

### Paso 10: Verificar Frontend
```bash
docker logs arriendos-frontend
curl -s http://<IP_PROD>:83/
```

---

## 6. ROLLBACK

Si algo falla, volver a la version anterior usando imagenes Docker.

### Rollback rapido (si el codigo cambio pero la BD esta bien)

#### Backend
```bash
# Detener contenedor actual
docker stop arriendos-app && docker rm arriendos-app

# Arrancar con imagen anterior (usar tag del backup)
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/logs:/app/logs \
  arriendos:backup-YYYYMMDD_HHMM

# Verificar
docker logs arriendos-app
```

#### Frontend
```bash
# Detener contenedor actual
docker stop arriendos-frontend && docker rm arriendos-frontend

# Arrancar con imagen anterior
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  arriendos-frontend:backup-YYYYMMDD_HHMM

# Verificar
docker logs arriendos-frontend
```

### Rollback con restauracion de BD (si migrate corrompio datos)

```bash
# 1. Rollback codigo (mismo que arriba)
docker stop arriendos-app && docker rm arriendos-app
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/logs:/app/logs \
  arriendos:backup-YYYYMMDD_HHMM

# 2. Restaurar BD
pg_restore -h <DB_HOST> -p <DB_PORT> -U <DB_USER> -d <DB_NAME> -c backup_pre_migracion.dump

# 3. Verificar
docker logs arriendos-app
curl http://<IP>:9005/swagger/
```

### Listar imagenes disponibles para rollback
```bash
# Backend
docker images arriendos --format "table {{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"

# Frontend
docker images arriendos-frontend --format "table {{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"
```

---

## 7. SCRIPTS DE DESPLIEGUE

### deploy.sh (para el servidor)

Crear `/home/<user>/deploy.sh`:

```bash
#!/bin/bash
set -e

echo "========================================="
echo "  DESPLIEGUE - $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# Taggear version actual
echo "1. Taggeando version actual..."
docker tag arriendos:latest arriendos:backup-$(date +%Y%m%d_%H%M) 2>/dev/null || true
docker tag arriendos-frontend:latest arriendos-frontend:backup-$(date +%Y%m%d_%H%M) 2>/dev/null || true

# Desplegar backend
echo "2. Despleguing backend..."
docker build -t arriendos:latest .
docker stop arriendos-app 2>/dev/null || true
docker rm arriendos-app 2>/dev/null || true
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/logs:/app/logs \
  arriendos:latest

# Desplegar frontend
echo "3. Despleguing frontend..."
cd ../arriendos-frontend
docker build -t arriendos-frontend:latest .
docker stop arriendos-frontend 2>/dev/null || true
docker rm arriendos-frontend 2>/dev/null || true
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  arriendos-frontend:latest

echo "========================================="
echo "  Despliegue completado"
echo "========================================="
```

### rollback.sh (para el servidor)

Crear `/home/<user>/rollback.sh`:

```bash
#!/bin/bash
set -e

TAG=${1:-""}

if [ -z "$TAG" ]; then
    echo "Uso: ./rollback.sh <tag>"
    echo ""
    echo "Tags disponibles:"
    docker images arriendos --format "  {{.Tag}}"
    exit 1
fi

echo "========================================="
echo "  ROLLBACK a $TAG - $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# Rollback backend
echo "1. Rollback backend..."
docker stop arriendos-app 2>/dev/null || true
docker rm arriendos-app 2>/dev/null || true
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  arriendos:$TAG

# Rollback frontend
echo "2. Rollback frontend..."
docker stop arriendos-frontend 2>/dev/null || true
docker rm arriendos-frontend 2>/dev/null || true
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  arriendos-frontend:$TAG

echo "========================================="
echo "  Rollback completado"
echo "========================================="
```

### Uso
```bash
# Desplegar
chmod +x deploy.sh
./deploy.sh

# Rollback
chmod +x rollback.sh
./rollback.sh backup-20260805_1600
```

---

## 8. CHECKLIST DE DESPLIEGUE SEGURO

### Fase 1: Preparacion (ANTES de tocar nada)

| Paso | Que hacer | Comando |
|------|-----------|---------|
| 1 | Backup de BD | `pg_dump ... backup_pre_migracion.dump` |
| 2 | Verificar backup | `pg_restore -l backup_pre_migracion.dump > /dev/null` |
| 3 | Taggear imagen backend | `docker tag arriendos:latest arriendos:backup-$(date +%Y%m%d_%H%M)` |
| 4 | Taggear imagen frontend | `docker tag arriendos-frontend:latest arriendos-frontend:backup-$(date +%Y%m%d_%H%M)` |
| 5 | Comunicar ventana | (si aplica) |

### Fase 2: Despliegue

| Paso | Que hacer | Comando |
|------|-----------|---------|
| 6 | Actualizar codigo | `git pull origin dev-roles` |
| 7 | Construir backend | `docker build -t arriendos:latest .` |
| 8 | Desplegar backend | `docker run -d --name arriendos-app ...` |
| 9 | Verificar backend | `docker logs arriendos-app && curl .../swagger/` |
| 10 | Construir frontend | `docker build -t arriendos-frontend:latest .` |
| 11 | Desplegar frontend | `docker run -d --name arriendos-frontend ...` |
| 12 | Verificar frontend | `docker logs arriendos-frontend && curl .../` |

### Fase 3: Post-despliegue

| Paso | Que hacer | Comando |
|------|-----------|---------|
| 13 | Login LDAP | Probar con usuario real |
| 14 | CRUD basico | Crear/ver un arriendo |
| 15 | Logs | `docker logs arriendos-app --tail 50` |
| 16 | Confirmar tablas | `docker exec arriendos-app python manage.py dbshell -c "\dt roles_*"` |

### Si algo falla: Rollback

| Paso | Que hacer | Comando |
|------|-----------|---------|
| 17 | Detener contenedor | `docker stop arriendos-app && docker rm arriendos-app` |
| 18 | Arrancar version anterior | `docker run -d ... arriendos:backup-YYYYMMDD_HHMM` |
| 19 | Si BD corrompida | `pg_restore -d <db> -c backup_pre_migracion.dump` |

---

## 9. TROUBLESHOOTING

### Error: "relation does not exist"
Las migraciones no se ejecutaron.
```bash
docker exec arriendos-app python manage.py migrate
```

### Error: "database does not exist"
La BD no fue creada.
```bash
createdb -h <DB_HOST> -p <DB_PORT> -U <DB_USER> <DB_NAME>
```

### Error: "could not connect to server"
El contenedor no puede alcanzar la BD.
```bash
docker exec arriendos-app python -c "
import psycopg2
conn = psycopg2.connect(host='<DB_HOST>', port='<DB_PORT>', dbname='<DB_NAME>', user='<DB_USER>', password='<DB_PASSWORD>')
print('BD OK')
conn.close()
"
```

### El contenedor se reinicia constantemente
```bash
docker logs arriendos-app
```
Causas comunes:
- Error en `.env` (variable faltante o incorrecta)
- Error de conexion a BD
- Migraciones pendientes que fallan

### LDAP no funciona
```bash
# Verificar LDAP_STATUS=True en .env
docker exec arriendos-app python -c "from django.conf import settings; print(settings.LDAP_STATUS)"

# Verificar conexion LDAP
docker exec arriendos-app python -c "
from ldap3 import Server, Connection
server = Server('${LDAP_SERVER}')
conn = Connection(server, '${LDAP_USER}', '${LDAP_PASSWORD}')
print('LDAP OK' if conn.bind() else 'LDAP ERROR')
"
```

### Imagenes no cargan
```bash
docker exec arriendos-app python manage.py seed_images
```

### Logs no se crean
```bash
docker exec arriendos-app ls -la logs/
```

---

## VARIABLES DE ENTORNO — REFERENCIA RAPIDA

| Variable | Local | Pruebas | Produccion |
|----------|-------|---------|------------|
| `DB_HOST` | 127.0.0.1 | <IP_BD> | <IP_PROD> |
| `DB_PORT` | 5432 | 5438 | <PORT_PROD> |
| `DB_NAME` | bd_arriendos | <NOMBRE_BD> | <NAME_PROD> |
| `DB_USER` | postgres | test | <USER_PROD> |
| `DB_PASSWORD` | 123456 | <VERIFICAR> | <VERIFICAR> |
| `SECRET_KEY` | local-dev-key | <GENERAR> | <GENERAR> |
| `DEBUG` | True | True | **False** |
| `ENVIRONMENT` | local | development | **production** |
| `LDAP_STATUS` | False | True | True |
| `GUNICORN_WORKERS` | N/A | 2 | <SEGUN_CPU> |
