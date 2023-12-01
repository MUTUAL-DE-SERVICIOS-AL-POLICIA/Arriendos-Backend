# SOFTWARE DE ARRIENDO
## REQUISITOS
- PYTHON
- DJANGO
## INSTALACION
PASO 1: Copiar el proyecto de github
```
git clone https://github.com/MUTUAL-DE-SERVICIOS-AL-POLICIA/Arriendos-Backend.git
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
```
# DESPLIEGUE CON DOCKER
PASO 1: Construir la imagen con:
```
docker build -t arriendos:latest .
```
PASO 2: ejecutar el contenedor con:
```
 docker run -d -p 9005:9005 -v <ruta del proyecto>:<ruta en el contendor> arriendos
```