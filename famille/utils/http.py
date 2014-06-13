from contextlib import contextmanager
import json
import os

from django.contrib.auth.decorators import login_required as django_login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, Http404, HttpResponse
from django.views.decorators.http import require_POST

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
    from famille.models import get_user_related
    def wrapped(request, *args, **kwargs):
        try:
            request.related_user = get_user_related(request.user)
        except ObjectDoesNotExist:
            raise Http404
        return func(request, *args, **kwargs)
    return wrapped


@require_POST
def assert_POST(request):
    """
    Assert that a request is a POST request.
    """
    pass


class JsonResponse(HttpResponse):
    '''
    This helper class is dedicated to simplifying sending Json back to the client
    '''

    def __init__(self, content={}, status=200, **kwargs):
        '''
        Constructs an HttpResponse with the provided content transformed as Json
        Is equivalent to:
            HttpResponse(json.dumps(content), content_type='application/json', status)
        '''
        content = json.dumps(content, cls=JSONEncoder)
        super(JsonResponse, self).__init__(
            content, content_type='application/json', status=status, **kwargs
        )


@contextmanager
def use_proxy():
    """
    A context manager to use an HTTP proxy.
    """
    _http_proxy = os.environ.get("http_proxy")
    try:
        os.environ['http_proxy'] = os.environ['QUOTAGUARD_URL']
        yield
    finally:
        os.environ.pop("http_proxy")
        if _http_proxy:
            os.environ['http_proxy'] = _http_proxy
