# -*- coding=utf-8 -*-
import base64
from functools import partial
import logging
import json
import smtplib

from django.conf import settings
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
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
        kwargs["body"] = render_to_string(template_name, context)
        msg = mail.EmailMessage(**kwargs)
        msg.content_subtype = "html"
        try:
            return msg.send()
        except smtplib.SMTPException as e:
            return cls.on_failure(e)

    @classmethod
    def on_failure(cls, exc):
        """
        A callback when failure occurs.
        """
        logging.error("An error occured while sending an email: %s", exc)


send_mail_from_template = Mailer.send_mail_from_template
send_mail_from_template_with_contact = partial(send_mail_from_template, from_email=settings.CONTACT_EMAIL)
send_mail_from_template_with_noreply = partial(send_mail_from_template, from_email=settings.NOREPLY_EMAIL)


def email_moderation(message):
    """
    Only allow email for premium users.

    :param message:       the message to be sent
    """
    from famille.models import get_user_related
    try:
        sender = get_user_related(message.sender)
    except (ObjectDoesNotExist, AttributeError):
        return (False, u"Votre compte ne vous permet pas d'envoyer d'email.")

    if not sender.is_premium:
        return (False, u"Vous devez avoir un compte premium pour accéder à cette fonctionnalité.")

    return True


def decode_recipient_list(data):
    """
    Decode a list of recipients.
    """
    data = data.split("---")
    return [json.loads(base64.urlsafe_b64decode(str(r))) for r in data]


def encode_recipient(recipient):
    """
    Encode a recipient using b64.
    """
    data = {
        "type": recipient.__class__.__name__,
        "pk": recipient.pk
    }
    return base64.urlsafe_b64encode(json.dumps(data))
