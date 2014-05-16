from django import template

from famille.forms import LANGUAGES


register = template.Library()


BADGE_FOLDER = "img/badges/%s.png"
FLAG_FOLDER = "img/flag/%s.png"


@register.filter(name='badge_icon')
def get_badge_icon(user, name):
    """
    Retrieve the badge icon url according to the value
    of the parameter (True or False).

    :param user:     the user
    :param name:     the name of the parameter
    """
    value = getattr(user, name)
    if not value:
        name = "no-%s" % name

    return BADGE_FOLDER % name


@register.filter(name='badge_icon_garde')
def get_badge_icon_garde(user, name):
    """
    Retrieve the badge icon url according to the value
    of the type of garde.

    :param user:     the user
    :param name:     the name of the parameter
    """
    if name != user.type_garde:
        name = "no-%s" % name

    return BADGE_FOLDER % name


@register.filter(name='language_icon')
def get_language_icon(user, value):
    """
    Retrieve the badge icon url according to the value
    of the language field.

    :param user:     the user
    :param value:    the value of the language
    """
    language = user.language or ""
    if value in language:
        return FLAG_FOLDER % value


@register.filter(name='language_display')
def get_language_display(value):
    """
    Retrieve the language display test from integer.
    """
    return LANGUAGES.get(value, "")
