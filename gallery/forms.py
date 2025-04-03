from django import forms
from products.widgets import CustomClearableFileInput
from .models import GalleryImage, Category


class GalleryForm(forms.ModelForm):
    """
    A form to handle the creation and editing of GalleryImage instances.

    """

    image = forms.ImageField(
        label="Image", required=True, widget=CustomClearableFileInput
    )

    class Meta:
        model = GalleryImage
        fields = ["title", "description", "category", "image"]

    def __init__(self, *args, **kwargs):
        """
        Initializes the form with category choices and applies a CSS
        class to each field's widget.

        Fetches all available categories and uses their friendly name for /
        the category field choices. Applies 'border-black' and 'rounded-0' /
        classes to each field widget for styling purposes.
        """
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields["category"].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "border-black rounded-0"
