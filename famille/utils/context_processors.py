from famille.models import has_user_related, get_user_related


def related_user(request):
    """
    A context processor that returns the related user from a request.user.

    :param request:        the request to be processed
    """
    if not has_user_related(request.user):
        return {}

    return {"related_user": get_user_related(request.user)}
