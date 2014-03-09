from functools import partial
import smtplib

from django.core.mail import send_mail
from django.template.loader import render_to_string


class Mailer(object):

    @classmethod
    def send_mail_from_template(cls, template_name, context, **kwargs):
        """
        Send an email given a template and a context. The other keyword
        arguments will be passed through send_mail method.

        :param template_name:           the name of the template to render
        :param context:                 the context to render the template
        """
        kwargs["message"] = render_to_string(template_name, context)
        try:
            return send_mail(**kwargs)
        except smtplib.SMTPException as e:
            return cls.on_failure(e)

    @classmethod
    def on_failure(cls, exc):
        """
        A callback when failure occurs.
        """
        # TODO
        pass


CONTACT_EMAIL = "contact@uneviedefamille.fr"
NOREPLY_EMAIL = "ne-pas-repondre@uneviedefamille.fr"

send_mail_from_template = Mailer.send_mail_from_template
send_mail_from_template_with_contact = partial(send_mail_from_template, from_email=CONTACT_EMAIL)
send_mail_from_template_with_noreply = partial(send_mail_from_template, from_email=NOREPLY_EMAIL)
