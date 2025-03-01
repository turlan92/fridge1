from django.apps import AppConfig


class Fr1Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fr1'

    def ready(self):
        import fr1.signals  # Подключаем сигналы
