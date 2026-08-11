# SOFTWARE DE ARRIENDO - Backend

Sistema de gestion de arriendos de ambientes de MUSERPOL. Backend desarrollado con Django 3.2 y DRF.

## Requisitos

- Python 3.10+
- PostgreSQL
- Docker (para despliegue)

---

## Inicio Rapido (Local)

### 1. Clonar y configurar
```bash
git clone https://github.com/MUTUAL-DE-SERVICIOS-AL-POLICIA/Arriendos-Backend.git
cd Arriendos-Backend
git checkout dev-roles
cp .env.example .env
# Editar .env con tus valores (ver .env.example para opciones)
```

### 2. Levantar con Docker
```bash
docker build -t arriendos:latest .
docker run -d \
  --name arriendos-app \
  --env-file .env \
  -p 9005:9005 \
  arriendos:latest
```

### 3. Verificar
- Swagger: `http://localhost:9005/swagger/`
- Logs: `docker logs arriendos-app`

---

## Despliegue

Para instrucciones detalladas de despliegue en local, pruebas y produccion, ver **[DESPLEGUE.md](DESPLEGUE.md)**.

---

## Estructura del Proyecto

```
Arriendos-Backend/
├── Arriendos_Backend/    # Configuracion Django
├── customers/            # Clientes
├── financials/           # Pagos y garantias
├── leases/               # Arriendos
├── login/                # Autenticacion (LDAP + local)
├── plans/                # Planes de descuento
├── products/             # Productos y tarifas
├── records/              # Auditoria
├── requirements/         # Requisitos documentales
├── roles/                # RBAC (roles y permisos)
├── rooms/                # Inmuebles y salones
├── users/                # Usuarios
├── seed_data/            # Datos semilla (imagenes)
├── .env.example          # Plantilla de variables de entorno
├── entrypoint.sh         # Script de inicio Docker
├── Dockerfile            # Configuracion Docker
└── DESPLEGUE.md          # Guia de despliegue completa
```

---

## Variables de Entorno

Toda la configuracion se controla via variables de entorno. Copia `.env.example` como `.env` y ajusta los valores.

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| `DB_HOST` | Host de PostgreSQL | `127.0.0.1` |
| `DB_PORT` | Puerto | `5432` |
| `DB_NAME` | Nombre de BD | `bd_arriendos` |
| `DB_USER` | Usuario BD | `postgres` |
| `DB_PASSWORD` | Password BD | `***` |
| `SECRET_KEY` | Clave Django | `<generar>` |
| `DEBUG` | Modo debug | `True` / `False` |
| `ENVIRONMENT` | Entorno | `local` / `development` / `production` |
| `LDAP_STATUS` | LDAP activo | `True` / `False` |
| `LDAP_SERVER` | URL del servidor LDAP | `ldap://ldap.tudominio.com:389` |
| `LDAP_USER` | Usuario administrador LDAP | `cn=admin,dc=tudominio,dc=com` |
| `LDAP_PASSWORD` | Password LDAP | `***` |

Ver `.env.example` para todas las variables disponibles.

---

## Comandos Utiles

```bash
# Ejecutar tests
docker exec -w /app/Arriendos-Backend arriendos-app python -m pytest tests/ -v

# Verificar migraciones
docker exec arriendos-app python manage.py migrate --check

# Crear superusuario
docker exec -it arriendos-app python manage.py createsuperuser

# Precargar imagenes
docker exec arriendos-app python manage.py seed_images
```
