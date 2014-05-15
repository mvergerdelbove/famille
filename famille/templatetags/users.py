from django import template


register = template.Library()


BADGE_FOLDER = "img/badges/%s.png"

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
