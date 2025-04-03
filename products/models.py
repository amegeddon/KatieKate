from django.db import models


class Category(models.Model):
    """
    A model representing a product category.
    """

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        """
        Returns the name of the category.
        """
        return self.name

    def get_friendly_name(self):
        """
        Returns the friendly name of the category.
        """
        return self.friendly_name


class SpecialOffer(models.Model):
    """
    A model representing a special offer or discount on products.

    The SpecialOffer model is used to associate specific offers with products.
    Offers may include discounts, promotions, etc.
    """

    name = models.CharField(max_length=50, unique=True)
    friendly_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.friendly_name if self.friendly_name else self.name


class Product(models.Model):
    """
    A model representing a product.
    """

    category = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.SET_NULL
    )
    special_offer = models.ForeignKey(
        "SpecialOffer", null=True, blank=True, on_delete=models.SET_NULL
    )
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
