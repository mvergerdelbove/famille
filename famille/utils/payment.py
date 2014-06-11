# -*- coding=utf-8 -*-
from datetime import date, timedelta
import logging

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import TimestampSigner, BadSignature
from django.core.urlresolvers import reverse
from paypal.standard.forms import PayPalPaymentsForm


logger = logging.getLogger(__name__)

PREMIUM_ID_TPL = "9b1818-%s%s"
PREMIUM_IDS = {
    "1f": PREMIUM_ID_TPL % ("f", "1"),
    "3f": PREMIUM_ID_TPL % ("f", "3"),
    "12f": PREMIUM_ID_TPL % ("f", "12"),
    "12p": PREMIUM_ID_TPL % ("p", "12"),
}

PRODUCTS = {
    "famille": [
        {
            "amount": "10.00",
            "item_title": u"Découverte",
            "item_frequence": "/mois",
            "item_name": u"Abonnement Illimité pendant 1 mois",
            "item_number": PREMIUM_IDS["1f"],
            "button_type": PayPalPaymentsForm.BUY
        },
        {
            "amount": "7.00",
            "item_title": u"Liberté",
            "item_frequence": "/mois",
            "item_name": u"Abonnement Illimité pendant 3 mois",
            "item_number": PREMIUM_IDS["3f"],
            "button_type": PayPalPaymentsForm.SUBSCRIBE
        },
        {
            "amount": "5.00",
            "item_title": u"Serenité",
            "item_frequence": "/mois",
            "item_name": u"Abonnement Illimité pendant 1 an",
            "item_number": PREMIUM_IDS["12f"],
            "button_type": PayPalPaymentsForm.SUBSCRIBE
        }
    ],
    "prestataire": [
        {
            "amount": "5.00",
            "item_title": "Forfait",
            "item_frequence": u"pour toute l'année",
            "item_name": u"Abonnement Illimité pendant un an",
            "item_number": PREMIUM_IDS["12p"],
            "button_type": PayPalPaymentsForm.BUY
        }
    ]
}

BASE_PRODUCT_INFO = {
    "src": "1",
    "currency_code": "EUR",
    "business": settings.PAYPAL_RECEIVER_EMAIL,
}


def compute_expires_at(ipn):
    """
    Compute the expiration date of the payment.

    :param ipn:      the ipn object
    """
    for key, value in PREMIUM_IDS.iteritems():
        if ipn.item_number == value:
            number_of_months = int(key.replace("p", "").replace("f", ""))
            break
    else:
        raise ValueError("Invalid item number")

    delta = timedelta(weeks=52) if number_of_months == 12 else timedelta(days=number_of_months * 31)
    return date.today() + delta


def get_payment_forms(user, request):
    """
    Retrieve the payment forms for given user and request.

    :param user:      the user that wants to see the forms
    :param request:   a django HttpRequest
    """
    user_type = user.__class__.__name__.lower()
    products = PRODUCTS[user_type]
    forms = []
    for product in products:
        data = BASE_PRODUCT_INFO.copy()
        data.update(
            invoice=signer.sign_user(user),
            notify_url=request.build_absolute_uri(reverse('paypal-ipn')),
            return_url=request.build_absolute_uri('/devenir-premium/succes/'),
            cancel_return=request.build_absolute_uri('/devenir-premium/annuler/'),
            **product
        )
        forms.append(PayPalPaymentsForm(button_type=product["button_type"], initial=data))
    return forms


class PaymentSigner(TimestampSigner):
    SEP = ":"
    PREFIX = "VDF_"

    def __init__(self, sep=SEP):
        super(PaymentSigner, self).__init__(sep=sep, salt="famille.payment")

    def sign_user(self, user):
        """
        Sign a given user.

        :param user:     the user, famille or prestataire
        """
        return self.sign("%s%s" % (user.PAYMENT_PREFIX, user.pk))

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
        if ipn.item_number not in PREMIUM_IDS.values():
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
        from famille import models
        value = self.unsign(ipn.invoice)

        prefix, pk = value[0], value[1:]
        ModelClass = models.Famille if prefix == models.Famille.PAYMENT_PREFIX else models.Prestataire
        return ModelClass.objects.get(pk=pk)

    def premium_signup(self, sender, **kwargs):
        """
        This method is a callback for django paypal signal,
        it links the payment to the user and mark the user as premium.
        """
        logger.info("Premium signup...")
        if self.transaction_is_legit(sender):
            user = self.user_from_ipn(sender)
            user.ipn_id = sender.pk
            user.plan = user.PLANS["premium"]
            user.plan_expires_at = compute_expires_at(sender)
            user.save()
        else:
            logger.warning("Paypal transaction not legit, pk %s", sender.pk)


signer = PaymentSigner()
