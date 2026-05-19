from django.apps import AppConfig

class BrowseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.browse'
    label = 'browse'
    verbose_name = 'Browse Material Catalog'
