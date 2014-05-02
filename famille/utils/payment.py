import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import TimestampSigner, BadSignature

from famille import models


class PaymentSigner(TimestampSigner):
    SEP = ":"
    PREFIX = "VDF_"
    FAMILLE_PREFIX = "f"
    PRESTA_PREFIX = "p"

    def __init__(self, sep=SEP):
        super(PaymentSigner, self).__init__(sep=sep, salt="famille.payment")

    def sign_user(self, user):
        """
        Sign a given user.

        :param user:     the user, famille or prestataire
        """
        prefix = self.FAMILLE_PREFIX if isinstance(user, models.Famille) else self.PRESTA_PREFIX
        return self.sign("%s%s" % (prefix, user.pk))

    def sign(self, value):
        """
        Sign a value. It prepends it a prefix.

        :param value:     the value to sign
        """
        value = "%s%s" % (self.PREFIX, value)
        return super(PaymentSigner, self).sign(value)

    def unsign(self, signed_value):
        """
        Unsign a value. It removes the prepended prefix.

        :param signed_value:     the value to unsign
        """
        value = super(PaymentSigner, self).unsign(signed_value)
        return value[len(self.PREFIX):]

    def transaction_is_legit(self, ipn):
        """
        Find out if a transaction is legit, i.e.
        verify the item number and that the invoice
        has the right format.

        :param ipn:            the ipn that fired a signal
        """
        if ipn.item_number != settings.PREMIUM_ID:
            return False

        try:
            value = self.unsign(ipn.invoice)
        except BadSignature:
            return False

        return True

    def user_from_ipn(self, ipn):
        """
        Return the user instance (Famille or Prestataire)
        for the IPN.

        :param ipn:            the ipn that fired a signal
        """
        value = self.unsign(ipn.invoice)

        prefix, pk = value[0], value[1:]
        ModelClass = models.Famille if prefix == self.FAMILLE_PREFIX else models.Prestataire
        return ModelClass.objects.get(pk=pk)

    def premium_signup(self, sender, **kwargs):
        """
        This method is a callback for django paypal signal,
        it links the payment to the user and mark the user as premium.
        """
        if self.transaction_is_legit(sender):
            user = self.user_from_ipn(sender)
            user.ipn_id = sender.pk
            user.plan = models.UserInfo.PLANS["premium"]
            user.save()
        else:
            logging.warning("Paypal transaction not legit, pk %s", sender.pk)


signer = PaymentSigner()
