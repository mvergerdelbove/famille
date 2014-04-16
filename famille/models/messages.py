from django.contrib.auth.models import User
from django.db import models

from famille.models.base import BaseModel


__all__ = ["Message", "get_inbox", "get_outbox"]


def get_outbox(related_user):
    """
    Return the messages contained in a user outbox.

    :param related_user:       a prestataire or a famille instance
    """
    return related_user.user.sent_messages.all()


def get_inbox(related_user):
    """
    Return the messages contained in a user inbox.

    :param related_user:       a prestataire or a famille instance
    """
    return related_user.user.received_messaged.all()


class Message(BaseModel):
    sender = models.ForeignKey(User, related_name="sent_messages")
    recipients = models.ManyToManyField(User, related_name="received_messaged")
    subject = models.CharField(blank=True, null=True, max_length=50)
    content = models.TextField(blank=True, null=True)
    sent = models.BooleanField(default=False)

    class Meta:
        app_label = 'famille'
