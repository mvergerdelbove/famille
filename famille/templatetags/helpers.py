from django import template


register = template.Library()


@register.filter(name='class_name')
def get_class_name(obj):
    """
    A simple template tag to retrieve the class name of
    an object.

    :param obj:           an input object
    """
    return obj.__class__.__name__
