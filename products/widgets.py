from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _


class CustomClearableFileInput(ClearableFileInput):
    """
    Custom widget to render a file input field with an option to remove the selected file.

    This custom widget extends the default ClearableFileInput widget and modifies
    the labels and template used to display the file input field. It provides a
    clearer option for users to remove the currently uploaded file and displays the
    current image when available.

    """
    clear_checkbox_label = _('Remove')
    initial_text = _('Current Image')
    input_text = _('')
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'
