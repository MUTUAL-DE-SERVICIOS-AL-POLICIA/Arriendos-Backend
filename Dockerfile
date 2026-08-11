FROM python:3.10

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "setuptools<81"
RUN pip install --no-cache-dir gunicorn

COPY . /app/

EXPOSE 9005

ENV DJANGO_SETTINGS_MODULE=Arriendos_Backend.settings
ENV ENVIRONMENT=development

HEALTHCHECK --interval=30s --timeout=10s --retries=5 --start-period=60s \
    CMD pgrep gunicorn > /dev/null || exit 1

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
