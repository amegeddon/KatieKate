from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_gallery_images, name='gallery'),  
    #path('add/', views.add_gallery_image, name='add_gallery_image'),
    #path('<int:gallery_image_id>/delete/', views.delete_gallery_image, name='delete_gallery_image'),
]
