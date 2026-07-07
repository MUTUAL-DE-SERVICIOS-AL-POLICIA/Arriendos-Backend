from django.apps import AppConfig


class RecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'records'
    verbose_name = 'Registros'

    def ready(self):
        import records.signals
