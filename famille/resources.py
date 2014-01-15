from tastypie.resources import ModelResource, ALL

from famille import models


class PrestataireResource(ModelResource):
    class Meta:
        queryset = models.Prestataire.objects.all()
        resource_name = "prestataires"
        excludes = ['user', "street", "tel", "tel_visible", "email"]
        allowed_methods = ["get", ]
