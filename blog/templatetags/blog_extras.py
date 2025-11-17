from django import template

register = template.Library()


@register.filter(name='split')
def split(value, sep=None):
    """Split a string by the given separator and return a list.

    Usage in templates:
        {% for item in mystring|split:"," %}
            {{ item }}
        {% endfor %}

    If value is already a list/tuple, returns it unchanged.
    """
    if value is None:
        return []
    # If it's already an iterable (list/tuple), just return it
    if isinstance(value, (list, tuple)):
        return value
    try:
        s = str(value)
    except Exception:
        return []
    if sep is None:
        return s.split()
    return [part.strip() for part in s.split(sep) if part.strip()]


@register.filter(name='strip')
def strip_filter(value):
    """Strip leading/trailing whitespace from a string.

    Usage in templates: {{ mystring|strip }}
    """
    if value is None:
        return ''
    try:
        return str(value).strip()
    except Exception:
        return value
