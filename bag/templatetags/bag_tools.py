from django import template


register = template.Library()

@register.filter(name='calc_subtotal')
def calc_subtotal(price, quantity):
    if not price or not quantity:
        return 0  # Return 0 if either price or quantity is missing
    return price * quantity


 # this function currently not working 