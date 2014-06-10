import re

from django.conf import settings


def get_context(**kwargs):
    """
    Minimum context configuration for all the templates.
    """
    kwargs.update(
        site_title="Une vie de famille",
        contact={
            "mail": settings.CONTACT_EMAIL,
            "address": settings.CONTACT_ADDRESS,
            "phone": settings.CONTACT_PHONE,
        }
    )
    return kwargs


def get_result_template_from_user(request, search_type="prestataire"):
    """
    Retrieve the template name to display the
    search results from the request. It will
    depend on the user right to see some / all
    parts of the results.

    :param request:          an HTTP request
    :param search_type:      famille or prestataire
    """
    return "search/results/%s.html" % search_type


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


def get_overlap(a, b):
    """
    Retrieve the overlap of two intervals
    (number of values common to both intervals).
    a and b are supposed to be lists of 2 elements.
    """
    return max(-1, min(a[1], b[1]) - max(a[0], b[0]) + 1)


IMAGE_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png"
}

DOCUMENT_TYPES = {
    ".doc": "application/msword",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pages": "application/x-iwork-pages-sffpages"
}
