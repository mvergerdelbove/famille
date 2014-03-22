from django.db.models.signals import pre_save

from famille import models

# disconnecting signal to not alter testing and flooding google
pre_save.disconnect(sender=models.Famille, dispatch_uid="famille_geolocate")
pre_save.disconnect(sender=models.Prestataire, dispatch_uid="prestataire_geolocate")
