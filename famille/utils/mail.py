from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_mail_from_template(template_name, context, **kwargs):
    """
    Send an email given a template and a context. The other keyword
    arguments will be passed through send_mail method.

    :param template_name:           the name of the template to render
    :param context:                 the context to render the template
    """
    kwargs["message"] = render_to_string(template_name, context)
    return send_mail(**kwargs)
