from django import template

from famille import data


register = template.Library()


BADGE_FOLDER = "img/badges/%s.png"
FLAG_FOLDER = "static/img/flag/%s.png"


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
def get_badge_icon_garde(user, value):
    """
    Retrieve the badge icon url according to the value
    of the type of garde.

    :param user:     the user
    :param value:     the value of the parameter
    """
    garde = user.type_garde or ""
    if value not in garde:
        value = "no-%s" % value

    return BADGE_FOLDER % value


LANGUAGES_TPL = """
<div class="col-md-3 col-md-offset-1 little-padding">
    <img src="%s" width="100%%;"
        data-toggle="tooltip" data-original-title="%s"/>
</div>
"""

@register.simple_tag(name="languages_html")
def get_languages_html(languages):
    """
    Display the HTML for languages.
    """
    if not languages:
        return ""

    html = ""
    languages = languages or ""
    languages = languages.split(",")
    for l in languages:
        src = FLAG_FOLDER % l
        disp = get_language_display(l)
        html += LANGUAGES_TPL % (src, disp)

    return html


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


display_dicts = {
    "language": data.LANGUAGES_DICT,
    "type_garde": data.TYPES_GARDE_DICT,
    "diploma": data.DIPLOMA_DICT,
    "experience_type": data.EXP_TYPES_DICT
}


@register.filter(name='language_display')
def get_language_display(value):
    """
    Retrieve the language display test from integer.
    """
    return data.LANGUAGES_DICT.get(value, u"")


@register.simple_tag(name="multi_display")
def get_multi_display(value, name):
    """
    Retrieve the display for a multi value field.

    :param value:    the value to display
    :param name:     the name of the field
    """
    if name not in display_dicts:
        return "--"
    data_dict = display_dicts[name]
    value = value or ""
    disps = []

    for v in value.split(","):
        disp = data_dict.get(v, "")
        if disp:
            disps.append(disp)

    return u", ".join(disps) or "--"
