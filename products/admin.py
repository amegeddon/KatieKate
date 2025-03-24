from django.contrib import admin
from .models import Product, Category, SpecialOffer

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'special_offer',  # Display the special offer in the admin list
        'price',
        'rating',
        'image',
    )
    ordering = ('sku',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )
    # Remove special_offer from list_filter because it does not belong to Category
    list_filter = ('name',)  # Only filter by category name or other relevant fields.

class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register models to the admin interface
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SpecialOffer, SpecialOfferAdmin)
