from django.apps import AppConfig


class CcConfig(AppConfig):
    name = 'cc'

    def ready(self):
        from .signals import user_save_handler
