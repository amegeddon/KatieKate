from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from products.widgets import CustomClearableFileInput

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label="Your Name")
    email = forms.EmailField(label="Your Email")
    message = forms.CharField(widget=forms.Textarea, label="Your Message")
    image = forms.ImageField(label='Image', required=False, widget=CustomClearableFileInput)  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'  
        self.helper.add_input(Submit('submit', 'Send Message'))
