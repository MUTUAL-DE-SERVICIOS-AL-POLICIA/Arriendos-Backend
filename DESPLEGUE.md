# DESPLIEGUE — ARRIENDOS

Guia para desplegar Backend y Frontend en cualquier entorno.

---

## TABLA DE CONTENIDOS

1. [Arquitectura](#1-arquitectura)
2. [Requisitos Previos](#2-requisitos-previos)
3. [Despliegue desde cero](#3-despliegue-desde-cero)
4. [Actualizacion (pull + rebuild)](#4-actualizacion)
5. [Rollback](#5-rollback)
6. [Scripts](#6-scripts)
7. [Checklist](#7-checklist)
8. [Troubleshooting](#8-troubleshooting)
9. [Variables de Entorno](#9-variables-de-entorno)

---

## 1. ARQUITECTURA

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Frontend       │────▶│  Backend        │────▶│  PostgreSQL     │
│  (React/Vite)   │     │  (Django)       │     │  (BD remota)    │
│  Puerto: 83     │     │  Puerto: 9005   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

- **Frontend:** React + TypeScript + Vite, servido por nginx
- **Backend:** Django 3.2 + DRF, corriendo con runserver (dev) o Gunicorn (prod)
- **BD:** PostgreSQL en servidor dedicado
- **LDAP:** Opcional, para autenticacion con Active Directory

---

## 2. REQUISITOS PREVIOS

- [ ] Docker instalado
- [ ] Acceso al repositorio Git
- [ ] Servidor PostgreSQL accesible
- [ ] (Opcional) Servidor LDAP accesible

### Generar SECRET_KEY
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 3. DESPLIEGUE DESDE CERO

### Paso 1: Clonar repositorios
```bash
git clone https://github.com/MUTUAL-DE-SERVICIOS-AL-POLICIA/Arriendos-Backend.git
git clone https://github.com/MUTUAL-DE-SERVICIOS-AL-POLICIA/arriendos-frontend.git
cd Arriendos-Backend
git checkout dev-roles
```

### Paso 2: Configurar Backend (.env)
```bash
cp .env.example .env
```

Editar `.env` con tus valores (ver [Variables de Entorno](#9-variables-de-entorno)):
```bash
# Generar SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Editar .env con:
# SECRET_KEY=<generar-arriba>
# DB_HOST=<IP_SERVIDOR_BD>
# DB_PORT=<PUERTO_BD>
# DB_NAME=<NOMBRE_BD>
# DB_USER=<USUARIO_BD>
# DB_PASSWORD=<PASSWORD_BD>
# ALLOWED_HOSTS=127.0.0.1,<IP_SERVIDOR>
# CORS_ORIGINS=http://<IP_SERVIDOR>:83
```

### Paso 3: Construir y levantar Backend
```bash
docker build -t arriendos:latest .
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/logs:/app/logs \
  arriendos:latest
```

> **IMPORTANTE:** Los volumenes `media` y `logs` son obligatorios. Sin ellos se pierden archivos y logs al recrear el contenedor.

### Paso 4: Verificar Backend
```bash
docker logs arriendos-app
# Abrir: http://<IP_SERVIDOR>:9005/swagger/
```

### Paso 5: Configurar Frontend
```bash
cd ../arriendos-frontend
git checkout dev-roles
```

Crear `.env` del frontend (esto es build-time, se quema en la imagen):
```bash
cat > .env << EOF
VITE_HOST_BACKEND="http://<IP_SERVIDOR>:9005/"
VITE_HOST='<IP_SERVIDOR>'
VITE_PORT='4300'
EOF
```

### Paso 6: Construir y levantar Frontend
```bash
docker build -t arriendos-frontend:latest .
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  -v $(pwd)/default.conf:/etc/nginx/conf.d/default.conf \
  arriendos-frontend:latest
```

### Paso 7: Verificar Frontend
```bash
docker logs arriendos-frontend
# Abrir: http://<IP_SERVIDOR>:83/
```

---

## 4. ACTUALIZACION

### Backend
```bash
cd /ruta/a/Arriendos-Backend

# Taggear version actual (rollback point)
docker tag arriendos:latest arriendos:backup-$(date +%Y%m%d_%H%M)

# Actualizar codigo
git pull origin dev-roles

# Reconstruir y reiniciar
docker build -t arriendos:latest .
docker stop arriendos-app && docker rm arriendos-app
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/logs:/app/logs \
  arriendos:latest

# Verificar
docker logs arriendos-app
```

### Frontend
```bash
cd /ruta/a/arriendos-frontend

# Taggear version actual
docker tag arriendos-frontend:latest arriendos-frontend:backup-$(date +%Y%m%d_%H%M)

# Actualizar codigo
git pull origin dev-roles

# Reconstruir y reiniciar
docker build -t arriendos-frontend:latest .
docker stop arriendos-frontend && docker rm arriendos-frontend
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  -v $(pwd)/default.conf:/etc/nginx/conf.d/default.conf \
  arriendos-frontend:latest

# Verificar
docker logs arriendos-frontend
```

---

## 5. ROLLBACK

### Rollback rapido (solo codigo, BD intacta)
```bash
# Backend
docker stop arriendos-app && docker rm arriendos-app
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/logs:/app/logs \
  arriendos:backup-YYYYMMDD_HHMM

# Frontend
docker stop arriendos-frontend && docker rm arriendos-frontend
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  arriendos-frontend:backup-YYYYMMDD_HHMM
```

### Rollback con restauracion de BD
```bash
# 1. Rollback codigo (usar comandos de arriba)

# 2. Restaurar BD
pg_restore -h <DB_HOST> -p <DB_PORT> -U <DB_USER> -d <DB_NAME> -c backup_pre_migracion.dump

# 3. Verificar
docker logs arriendos-app
```

### Listar imagenes disponibles
```bash
docker images arriendos --format "table {{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"
docker images arriendos-frontend --format "table {{.Tag}}\t{{.CreatedAt}}\t{{.Size}}"
```

---

## 6. SCRIPTS

### deploy.sh
```bash
#!/bin/bash
set -e

echo "DESPLIEGUE - $(date '+%Y-%m-%d %H:%M:%S')"

# Taggear version actual
docker tag arriendos:latest arriendos:backup-$(date +%Y%m%d_%H%M) 2>/dev/null || true
docker tag arriendos-frontend:latest arriendos-frontend:backup-$(date +%Y%m%d_%H%M) 2>/dev/null || true

# Backend
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

# Frontend
cd ../arriendos-frontend
docker build -t arriendos-frontend:latest .
docker stop arriendos-frontend 2>/dev/null || true
docker rm arriendos-frontend 2>/dev/null || true
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  arriendos-frontend:latest

echo "Despliegue completado"
```

### rollback.sh
```bash
#!/bin/bash
set -e

TAG=${1:-""}
if [ -z "$TAG" ]; then
    echo "Uso: ./rollback.sh <tag>"
    docker images arriendos --format "  {{.Tag}}"
    exit 1
fi

echo "ROLLBACK a $TAG - $(date '+%Y-%m-%d %H:%M:%S')"

# Backend
docker stop arriendos-app 2>/dev/null || true
docker rm arriendos-app 2>/dev/null || true
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/logs:/app/logs \
  arriendos:$TAG

# Frontend
docker stop arriendos-frontend 2>/dev/null || true
docker rm arriendos-frontend 2>/dev/null || true
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  arriendos-frontend:$TAG

echo "Rollback completado"
```

---

## 7. CHECKLIST

### Pre-despliegue
- [ ] Backup de BD verificado (`pg_dump` + `pg_restore -l`)
- [ ] Imagenes taggeadas (`docker tag`)
- [ ] Tests pasando
- [ ] Ventana comunicada (si aplica)

### Despliegue
- [ ] `git pull origin dev-roles`
- [ ] Backend: `docker build` + `docker run` + verificar `docker logs`
- [ ] Frontend: `docker build` + `docker run` + verificar `docker logs`
- [ ] Login LDAP probado
- [ ] CRUD basico probado

### Post-despliegue
- [ ] Logs sin errores: `docker logs arriendos-app --tail 50`
- [ ] Tablas RBAC creadas: `docker exec arriendos-app python manage.py dbshell -c "\dt roles_*"`

---

## 8. TROUBLESHOOTING

### "relation does not exist"
Migraciones no ejecutadas:
```bash
docker exec arriendos-app python manage.py migrate
```

### "database does not exist"
BD no creada:
```bash
createdb -h <DB_HOST> -p <DB_PORT> -U <DB_USER> <DB_NAME>
```

### "could not connect to server"
Contenedor no alcanza la BD. Verificar `.env`:
```bash
docker exec arriendos-app env | grep DB_
```

### Contenedor se reinicia constantemente
```bash
docker logs arriendos-app
```
Causas: error en `.env`, BD inaccesible, migraciones fallidas.

### LDAP no funciona
```bash
# Verificar LDAP_STATUS=True en .env
docker exec arriendos-app env | grep LDAP

# Probar conexion LDAP
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

### Frontend no conecta al Backend
Verificar `default.conf` de nginx apunta a la IP correcta del backend:
```bash
docker exec arriendos-frontend cat /etc/nginx/conf.d/default.conf
# Debe tener: proxy_pass http://<IP_SERVIDOR>:9005;
```

---

## 9. VARIABLES DE ENTORNO

Ver `.env.example` para la lista completa. Aqui las variables criticas:

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta Django (generar con `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`) | `abc123...` |
| `DEBUG` | True=desarrollo, False=produccion | `True` |
| `ALLOWED_HOSTS` | IPs/dominios permitidos, separados por coma | `127.0.0.1,192.168.1.100` |
| `CORS_ORIGINS` | URLs del frontend permitidas, separadas por coma | `http://192.168.1.100:83` |
| `ENVIRONMENT` | `development` (runserver) o `production` (Gunicorn) | `development` |
| `DB_HOST` | IP del servidor PostgreSQL | `192.168.1.200` |
| `DB_PORT` | Puerto PostgreSQL | `5432` |
| `DB_NAME` | Nombre de la BD | `bd_arriendos` |
| `DB_USER` | Usuario de BD | `postgres` |
| `DB_PASSWORD` | Password de BD | `tu_password` |
| `LDAP_STATUS` | Activar autenticacion LDAP | `False` |
| `LDAP_SERVER` | URL del servidor LDAP | `ldap://192.168.1.10:3891` |
| `LDAP_USER` | Bind DN del admin LDAP | `cn=admin,dc=empresa,dc=gob,dc=bo` |
| `LDAP_PASSWORD` | Password del admin LDAP | `tu_password_ldap` |
| `LDAP_USER_DN` | DN donde buscar usuarios | `ou=usuarios,dc=empresa,dc=gob,dc=bo` |
| `LDAP_BASE` | Base DN para busquedas | `dc=empresa,dc=gob,dc=bo` |
| `GUNICORN_WORKERS` | Workers de Gunicorn (solo prod) | `2` (1 por CPU + 1) |
