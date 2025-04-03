from django.urls import path
from . import views

urlpatterns = [
    path("", views.all_gallery_images, name="gallery"),
    path("add/", views.add_gallery_image, name="add_gallery_image"),
    path(
        "gallery/edit/<int:image_id>/",
        views.edit_gallery_image,
        name="edit_gallery_image",
    ),
    path(
        "delete/<int:image_id>/",
        views.delete_gallery_image,
        name="delete_gallery_image",
    ),
    path("image/<int:image_id>/", views.gallery_detail, name="gallery_detail"),
    path(
        "gallery/full-view/<int:image_id>/",
        views.gallery_full_view,
        name="gallery_full_view",
    ),
]
