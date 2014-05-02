from paypal.standard.ipn.signals import payment_was_successful

from .utils.payment import signer

# signals
payment_was_successful.connect(signer.premium_signup)
