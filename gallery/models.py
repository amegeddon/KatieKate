from django.db import models
from products.models import Category


class GalleryImage(models.Model):
    """
    A model representing an image in the gallery.

    This model includes fields for the title, description, image file,/
    creation timestamp, and a foreign key to the category to which the image /
    belongs.

    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="gallery/")
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="gallery_images",
    )

    def __str__(self):
        return self.title
