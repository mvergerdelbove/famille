from django.db.models.signals import pre_save

from famille import models
from famille.utils import threading


@threading.async
def geolocate(sender, instance, **kwargs):
    """
    A signal receiver to geolocate a user whenever its
    data is saved.
    """
    if not instance.geolocation and any((instance.postal_code, instance.city)):
        instance.geolocate()

pre_save.connect(geolocate, sender=models.Famille, dispatch_uid="famille_geolocate")
pre_save.connect(geolocate, sender=models.Prestataire, dispatch_uid="prestataire_geolocate")
