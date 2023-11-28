# gunicorn_config.py
bind = "0.0.0.0:9005"
workers = 10
module = "Arriendos_Backend.wsgi:application"
