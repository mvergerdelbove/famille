# -*- coding=utf-8 -*-
from django import template

from famille.forms import RatingFamilleForm, RatingPrestataireForm
from famille.models import (
    get_user_related, has_user_related, FamilleRatings,
    PrestataireRatings, Famille
)

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
    Returns True if user has related user or not.
    """
    return has_user_related(value)


@register.filter(name="get_related")
def get_related(value):
    """
    Returns the related user of a request.user.
    """
    return get_user_related(value)


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


@register.filter(name='plan')
def get_plan(user):
    """
    Return the plan of user.
    """
    if not has_user_related(user):
        return ""

    return get_user_related(user).plan


@register.filter(name='rating_form')
def get_rating_form(profile, request_user):
    """
    Return the rating form instance for a profile and
    a given user. Return None in case of a problem
    or the request user already voted.

    :param profile:        the profile to be rated
    :param request_user:   the request user
    """
    if isinstance(profile, Famille):
        RatingClass = FamilleRatings
        RatingFormClass = RatingFamilleForm
    else:
        RatingClass = PrestataireRatings
        RatingFormClass = RatingPrestataireForm

    if has_user_related(request_user):
        related_user = get_user_related(request_user)
        if not RatingClass.user_has_voted_for(related_user, profile):
            rating = RatingClass(user=profile, by=related_user.simple_id)
            return RatingFormClass(instance=rating)
    return None


@register.filter(name='display_tarif')
def display_tarif(tarif):
    """
    Display the tarif range.

    :param tarif:       comma separated range of tarif
    """
    if not tarif:
        return "--"

    return u"de %s à %s" % tuple(tarif.split(","))


@register.filter(name="contains")
def contains(value, arg):
    """
    Returns True if arg in value.
    """
    value = value or ""
    arg = arg or ""
    return arg in value
