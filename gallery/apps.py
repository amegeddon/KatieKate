from django.apps import AppConfig


class GalleryConfig(AppConfig):
    """
    Configuration class for the 'gallery' app. It defines the default
    auto field type and the name of the app within the Django project.

    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery'
