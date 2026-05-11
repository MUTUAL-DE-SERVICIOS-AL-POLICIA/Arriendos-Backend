# SOFTWARE DE ARRIENDOS (Backend)

Sistema de gestión de arriendos que permite el registro de inmuebles, arrendatarios y contratos de arrendamiento, además del control de pagos y la generación de consultas administrativas. Está desarrollado en Django y puede ejecutarse tanto en entornos locales como mediante Docker, lo que facilita su despliegue y portabilidad en distintos ambientes.

Guía rápida para levantar el backend de **Arriendos**.

## Formas de ejecución

Puedes ejecutar el proyecto de dos maneras:

1. **Sin Docker**
2. **Con Docker**

---

### Despliegue Sin DOCKER   

## REQUISITOS
- PYTHON
- DJANGO

## INSTALACION
PASO 1: Hacer el fork al proyecto desde GitHub
```
https://github.com/MUTUAL-DE-SERVICIOS-AL-POLICIA/Arriendos-Backend.git
```
PASO  2: verificar si tienes python instalado con
```
python3 -V
```
PASO 3: si no se tiene django instalar con
```
sudo apt install python3-django
```

PASO 4: instalar pip desde los repositorios oficiales
```
sudo apt install python3-pip
```
PASO 5: Instale el paquete venv para crear su entorno virtual
```
sudo apt install python3-venv
```
PASO 6: Una vez en la carpeta del proyecto, crea un entorno virtual para el proyecto si no lo has hecho ya. Puedes utilizar virtualenv o venv para crear un entorno virtual. Aquí tienes un ejemplo con venv:
```
python3 -m venv venv
```
Esto creará un entorno virtual llamado venv en la carpeta del proyecto.

PASO 7 : Activa el entorno virtual. En Linux, puedes hacerlo con el siguiente comando:

```
source venv/bin/activate
```
PASO 8: Instala las dependencias del proyecto que se encuentran en el archivo requirements.txt. Puedes hacerlo utilizando pip:
```
pip install -r requirements.txt
```
Esto instalará todas las bibliotecas y paquetes necesarios para ejecutar el proyecto.

PASO 9: Asegúrate de que has configurado la base de datos en tu máquina local. Esto incluye crear una base de datos y crear el archivo settings.py del proyecto.

PASO 10: Aplica las migraciones con;
```
python3 manage.py migrate
```

PASO 11:Entra a initial_data
```
cd initial_data
```
PASO 12: corre el script load_data.py con:
```
python3 load_data.py <ip del server> <puerto>
### segunda forma ( dockerizando)

```

# Despligue con DOCKER
PASO 0: Posicionarse en la ruta del proyecto Arriendos-Backend
PASO 1: Construir la imagen con:
```
docker build -t arriendos:latest .
```
PASO 2: ejecutar el contenedor con:
```
 docker run -d -p 9005:9005 -v <ruta del proyecto>:<ruta en el contendor> arriendos
```