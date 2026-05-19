from django.apps import AppConfig

class MyRequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.my_request'
    label = 'my_request'
    verbose_name = 'Student Material Requests'
