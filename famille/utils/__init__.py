from itertools import islice
import re


def get_context(**kwargs):
    """
    Minimum context configuration for all the templates.
    """
    kwargs.update(site_title="Une vie de famille")
    return kwargs


def get_result_template_from_user(request):
    """
    Retrieve the template name to display the
    search results from the request. It will
    depend on the user right to see some / all
    parts of the results.

    :param request:          an HTTP request
    """
    return "simple_results.html"


def pick(d, *args):
    """
    Pick some keys on a given dictionary.

    :param d:       the dict
    :param args:    the keys to pick
    """
    res = {}
    getitem = d.getlist if hasattr(d, "getlist") else d.__getitem__
    for key in args:
        if key in d:
            res[key] = getitem(key)
    return res


def repeat_lambda(func, times):
    """
    A variant of itertools.repeat that
    yiels a new value given by func (basically
    a lambda yielding an instance).

    :param func:       a lambda function
    :param times:      the number of times the item is repeated
    """
    for i in xrange(times):
        yield func()


def isplit(iterable, index):
    """
    A variant of tee with n=2 with
    specification of the length of the
    first iterable. This will return
    iterable[:index], iterable[index:].

    :param iterable:     the iterable to split
    :parma index:        where to split
    """
    return islice(iterable, index), islice(iterable, index, None)


resource_pattern = re.compile("/api/v1/([a-z_-]+)s/([\d]+)/?")


def parse_resource_uri(resource_uri):
    """
    Parse a resource uri (like /api/v1/prestataires/1/) and return
    the resource type and the object id.
    """
    match = resource_pattern.search(resource_uri)
    if not match:
        raise ValueError("Value %s is not a resource uri." % resource_uri)

    return match.group(1), match.group(2)
