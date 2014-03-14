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
