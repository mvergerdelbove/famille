import json

from django.contrib.auth.decorators import login_required as django_login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, Http404, HttpResponse

from famille.models import get_user_related
from famille.utils.python import JSONEncoder


login_required = django_login_required(
    redirect_field_name="s", login_url="auth_login"
)


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


class JsonResponse(HttpResponse):
    '''
    This helper class is dedicated to simplifying sending Json back to the client
    '''

    def __init__(self, content='', status=200, **kwargs):
        '''
        Constructs an HttpResponse with the provided content transformed as Json
        Is equivalent to:
            HttpResponse(json.dumps(content), content_type='application/json', status)
        '''
        content = json.dumps(content, cls=JSONEncoder)
        super(JsonResponse, self).__init__(
            content, content_type='application/json', status=status, **kwargs
        )
