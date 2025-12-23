from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'apps.core'

def ready(self):
        # Este método se ejecuta cuando Django arranca
        import apps.core.utils.signals  # Esto activa las señales