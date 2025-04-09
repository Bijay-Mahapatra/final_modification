from django.apps import AppConfig

class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_auth'  # This must match the folder name
    label = 'custom_auth'  # Add this for unique identification