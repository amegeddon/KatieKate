from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from products.widgets import CustomClearableFileInput


class ContactForm(forms.Form):
    """
    A form for users to submit a contact message including their name, email,
    message, and an optional image. This form uses crispy-forms for styling /
    and layout.
    """

    name = forms.CharField(max_length=100, label="Your Name")
    email = forms.EmailField(label="Your Email")
    message = forms.CharField(widget=forms.Textarea, label="Your Message")
    image = forms.ImageField(
        label="Image", required=False, widget=CustomClearableFileInput
    )

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and sets up crispy-forms layout, including setting
        the form method and form enctype for handling file uploads.

        """
        super().__init__(*args, **kwargs)

        # Set up crispy-forms helper to customize form layout
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_enctype = (
            "multipart/form-data"  
        )

        # Add submit button with label 'Send Message'
        self.helper.add_input(Submit("submit", "Send Message"))
