from django.contrib import admin
from .models import Product, Category, SpecialOffer


class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Product models.

    This class customizes how Product instances are displayed in the Django admin
    interface, including which fields to display and the default ordering.
    """
    list_display = (
        'sku',  # Product's stock keeping unit
        'name',  # Name of the product
        'category',  # Category to which the product belongs
        'special_offer',  # Display the special offer in the admin list
        'price',  # Product's price
        'rating',  # Product's rating
        'image',  # Product's image
    )
    ordering = ('sku',)  # Default ordering by SKU


class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Category models.

    This class customizes how Category instances are displayed in the Django admin
    interface, including which fields to display and the available filters.
    """
    list_display = (
        'friendly_name',  # Display friendly name of the category
        'name',  # Category's internal name
    )
    list_filter = ('name',)  # Filter categories by their name


class SpecialOfferAdmin(admin.ModelAdmin):
    """
    Admin interface for managing SpecialOffer models.

    This class customizes how SpecialOffer instances are displayed in the Django admin
    interface, including the search fields.
    """
    list_display = ('name',)  # Display only the name of the special offer
    search_fields = ('name',)  # Enable search by the name of the special offer


# Register models to the admin interface
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SpecialOffer, SpecialOfferAdmin)
