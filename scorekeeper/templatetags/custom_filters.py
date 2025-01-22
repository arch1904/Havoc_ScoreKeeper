from django import template

register = template.Library()

@register.filter
def key(dictionary, key_name):
    """
    Retrieves a value from a dictionary using a key.
    """
    return dictionary.get(key_name)