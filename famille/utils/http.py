import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, Http404

from famille.models import get_user_related


def require_JSON(func):
    """
    A decorator that makes a view require
    JSON content in the request body.
    """
    def wrapped(request, *args, **kwargs):
        if "application/json" not in request.META["CONTENT_TYPE"]:
            return HttpResponseBadRequest("Response header should be application/json.")
        try:
            request.json = json.loads(request.body)
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Request body should be valid JSON.")
        return func(request, *args, **kwargs)
    return wrapped


def require_related(func):
    """
    A decorator that makes a view require a related user,
    i.e. a famille or a prestataire.
    """
    def wrapped(request, *args, **kwargs):
        try:
            request.related_user = get_user_related(request.user)
        except ObjectDoesNotExist:
            raise Http404
        return func(request, *args, **kwargs)
    return wrapped
