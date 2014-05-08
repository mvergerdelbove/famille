from django import template

from famille.models import get_user_related, has_user_related


register = template.Library()


@register.filter(name='class_name')
def get_class_name(obj):
    """
    A simple template tag to retrieve the class name of
    an object.

    :param obj:           an input object
    """
    return obj.__class__.__name__


@register.filter(name="get_range")
def get_range(value):
    """
    A simple template tag to retrieve a python range.

    :param value:      the length of the range
    """
    return range(int(value or 0))


@register.filter(name="substract")
def substract(value, arg):
    return int(value or 0) - int(arg or 0)


@register.filter(name="user_type")
def user_type(value):
    """
    Return the user type of a request.user object.
    """
    if not has_user_related(value):
        return False

    return get_user_related(value).__class__.__name__


@register.filter(name="has_related")
def has_related(value):
    """
    Returns if user has related user or not.
    """
    return has_user_related(value)


@register.filter(name='key')
def key(d, key_name):
    """
    Return the key of a dictionnary.
    """
    return d[key_name]

@register.filter(name='get_form_field')
def get_form_field(form, field_name):
    """
    Return a field of a form
    """
    return form[field_name]
