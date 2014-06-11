from famille.models import has_user_related, get_user_related
from famille.utils import get_context


def related_user(request):
    """
    A context processor that returns the related user from a request.user.

    :param request:        the request to be processed
    """
    if not has_user_related(request.user):
        return {}

    return {"related_user": get_user_related(request.user)}


def base(request):
    """
    Providing base variables.

    :param request:        the request to be processed
    """
    return get_context()
