FROM python:3.10

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt al contenedor en /app/
COPY requirements.txt /app/

# instala las dependencias del sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \ 
    && rm -rf /var/lib/apt/lists/*

# Crea y activa el entorno virtual
RUN python -m venv venv
RUN /bin/bash -c "source venv/bin/activate"

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido del directorio actual al contenedor en /app/
COPY . /app/

# Indica que la aplicación se ejecutará en el puerto 9005
EXPOSE 9005

# Define la variable de entorno para Django
ENV DJANGO_SETTINGS_MODULE=Arriendos_Backend.settings

# Instala Gunicorn

#RUN pip install gunicorn


#CMD ["gunicorn", "-c", "gunicorn_config.py", "Arriendos_Backend.wsgi:application"]
CMD ["python3","manage.py","runserver", "0.0.0.0:9005"]