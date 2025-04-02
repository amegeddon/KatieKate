# models.py
from django.db import models

class ContactRequest(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    image = models.ImageField(upload_to='contact_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Contact request from {self.name} ({self.email})"
