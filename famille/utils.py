
def get_context(**kwargs):
    """
    Minimum context configuration for all the templates.
    """
    kwargs.update(site_title="Un air de famille")
    return kwargs
