from django.apps import AppConfig


class FinancialsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'financials'
    def ready(self):
        import financials.signals