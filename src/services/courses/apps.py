from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'src.services.courses'
    verbose_name = 'Courses'
    verbose_name_plural = 'Courses'
    default_auto_config = 'django.db.models.BigAutoField'

    def ready(self):
        import src.services.users.signals
