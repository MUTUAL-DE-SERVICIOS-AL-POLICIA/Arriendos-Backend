# DESPLIEGUE — ARRIENDOS BACKEND

Guia paso a paso para desplegar el sistema en los 3 entornos.

---

## TABLA DE CONTENIDOS

1. [Arquitectura](#1-arquitectura)
2. [Requisitos Previos](#2-requisitos-previos)
3. [Despliegue Local (desde cero)](#3-despliegue-local)
4. [Despliegue en Pruebas](#4-despliegue-en-pruebas)
5. [Despliegue en Produccion](#5-despliegue-en-produccion)
6. [Rollback](#6-rollback)
7. [Troubleshooting](#7-troubleshooting)

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

### Paso 4: Levantar con Docker
```bash
docker build -t arriendos:latest .
docker run -d \
  --name arriendos-app \
  -e DB_HOST="127.0.0.1" \
  -e DB_NAME="bd_arriendos" \
  -e DB_USER="postgres" \
  -e DB_PASSWORD="123456" \
  -e SECRET_KEY="<tu-secret-key>" \
  -e DEBUG=True \
  -e ENVIRONMENT=local \
  -e LDAP_STATUS=False \
  -p 9005:9005 \
  arriendos:latest
```

### Paso 5: Verificar
```bash
# Ver logs
docker logs arriendos-app

# Abrir swagger
# http://localhost:9005/swagger/
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

---

## 4. DESPLIEGUE EN PRUEBAS

### Arquitectura del servidor de pruebas

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
pg_dump -h <IP_BD> -p 5438 -U test -d <NOMBRE_BD> -Fc -f /home/administrador/backup_pruebas_$(date +%Y%m%d_%H%M).dump
```

### Paso 3: Clonar o actualizar el codigo
```bash
cd /home/administrador/aplicaciones-dev/Arriendos/Arriendos-Backend
git fetch origin
git checkout dev-roles
git pull origin dev-roles
```

### Paso 4: Crear archivo .env
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

### Paso 5: Detener contenedor viejo
```bash
# Anotar image ID para rollback
docker inspect cranky_dijkstra --format '{{.Image}}' > /home/administrador/rollback_image.txt

# Detener y eliminar
docker stop cranky_dijkstra
docker rm cranky_dijkstra
```

### Paso 6: Construir y ejecutar nuevo contenedor
```bash
docker build -t arriendos:latest .
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  arriendos:latest
```

### Paso 7: Verificar
```bash
# Ver logs de arranque
docker logs arriendos-app

# Verificar swagger
curl -s http://<IP_SERVIDOR>:9005/swagger/

# Verificar login LDAP
curl -X POST http://<IP_SERVIDOR>:9005/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"<usuario_ldap>","password":"<password>"}'

# Verificar tablas nuevas
docker exec arriendos-app python manage.py dbshell -c "\dt roles_*"
```

### Paso 8: Actualizar frontend (si aplica)
```bash
cd /home/administrador/aplicaciones-dev/Arriendos/arriendos-frontend
git fetch origin
git checkout dev-roles
git pull origin dev-roles

# Crear .env
cat > .env << 'EOF'
VITE_HOST_BACKEND="http://<IP_SERVIDOR>:9005/"
VITE_HOST='<IP_SERVIDOR>'
VITE_PORT='4300'
EOF

# Reconstruir
docker build -t arriendos-frontend:latest .

# Detener viejo y arrancar nuevo
docker stop silly_euclid && docker rm silly_euclid
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  arriendos-frontend:latest
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
pg_dump -h <DB_HOST_PROD> -p <DB_PORT_PROD> -U <DB_USER_PROD> -d <DB_NAME_PROD> -Fc -f /home/<user>/backup_produccion_$(date +%Y%m%d_%H%M).dump
```

### Paso 3: Verificar backup
```bash
createdb -U postgres bd_test_restore
pg_restore -h localhost -U postgres -d bd_test_restore backup_produccion_*.dump
dropdb -U postgres bd_test_restore
```

### Paso 4: Clonar o actualizar el codigo
```bash
cd /home/<user>/aplicaciones/Arriendos/Arriendos-Backend
git fetch origin
git checkout dev-roles
git pull origin dev-roles
```

### Paso 5: Crear archivo .env para produccion
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

### Paso 6: Detener contenedor viejo
```bash
docker inspect <CONTAINER_NAME> --format '{{.Image}}' > /home/<user>/rollback_image.txt
docker stop <CONTAINER_NAME>
docker rm <CONTAINER_NAME>
```

### Paso 7: Construir y ejecutar nuevo contenedor
```bash
docker build -t arriendos:latest .
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  arriendos:latest
```

### Paso 8: Verificar
```bash
# Ver logs
docker logs arriendos-app

# Verificar swagger
curl -s http://<IP_PROD>:9005/swagger/

# Verificar login LDAP
curl -X POST http://<IP_PROD>:9005/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"<usuario>","password":"<password>"}'

# Verificar tablas nuevas
docker exec arriendos-app python manage.py dbshell -c "\dt roles_*"
```

### Paso 9: Actualizar frontend (si aplica)
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

# Reconstruir
docker build -t arriendos-frontend:latest .

# Detener viejo y arrancar nuevo
docker stop <FRONTEND_CONTAINER> && docker rm <FRONTEND_CONTAINER>
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  arriendos-frontend:latest
```

---

## 6. ROLLBACK

Si algo falla, volver a la version anterior:

### Backend
```bash
# Recuperar image ID del backup
IMAGE_ID=$(cat /home/<user>/rollback_image.txt)

# Detener contenedor actual
docker stop arriendos-app
docker rm arriendos-app

# Arrancar con imagen anterior
docker run -d \
  --name arriendos-app \
  --restart unless-stopped \
  --env-file .env \
  -p 9005:9005 \
  $IMAGE_ID
```

### Frontend
```bash
docker stop arriendos-frontend
docker rm arriendos-frontend

# Reconstruir desde la rama main (version anterior)
git checkout main
docker build -t arriendos-frontend:latest .
docker run -d \
  --name arriendos-frontend \
  --restart unless-stopped \
  -p 83:80 \
  arriendos-frontend:latest
```

### Restaurar BD (ULTIMO RECURSO)
```bash
# SOLO si la migracion corrompio datos
pg_restore -h <DB_HOST> -p <DB_PORT> -U <DB_USER> -d <DB_NAME> -c backup_*.dump
```

---

## 7. TROUBLESHOOTING

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
# Verificar conectividad
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
# Verificar que LDAP_STATUS=True en .env
docker exec arriendos-app python -c "from django.conf import settings; print(settings.LDAP_STATUS)"

# Verificar conexion al servidor LDAP
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
# Verificar que la carpeta logs existe
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
