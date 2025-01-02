from django.apps import AppConfig


class TreatmentAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'treatment_app'

    def ready(self):
        import treatment_app.signals  # This ensures signals are loaded
