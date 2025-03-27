from django import forms
from products.widgets import CustomClearableFileInput  
from .models import GalleryImage, Category

class GalleryForm(forms.ModelForm):
    image = forms.ImageField(label='Image', required=True, widget=CustomClearableFileInput)

    class Meta:
        model = GalleryImage
        fields = ['title', 'description', 'category', 'image']  # Include category

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
