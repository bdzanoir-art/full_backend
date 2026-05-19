from django.apps import AppConfig

class LoginAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.login_app'
    label = 'login_app'
    verbose_name = 'Login'
