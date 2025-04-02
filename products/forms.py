from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """
    A form for creating and updating Product instances.

    This form allows for the addition and modification of product details.
    It also customizes the display of the category choices and the image input field.
    """
    class Meta:
        model = Product
        fields = '__all__'

    image = forms.ImageField(
        label='Image',
        required=False,
        widget=CustomClearableFileInput
    )

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and customises the category choices.

        Fetches all categories from the database, creates a list of tuples
        containing category IDs and their friendly names, and sets the category
        field choices to this list. Also, adds styling classes to all form fields.
        """
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names

        # Apply a default CSS class to each field's widget
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
