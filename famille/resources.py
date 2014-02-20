from tastypie.resources import ModelResource, ALL

from famille import models, forms


class PrestataireResource(ModelResource):
    class Meta:
        queryset = models.Prestataire.objects.all()
        resource_name = "prestataires"
        excludes = ['user', "street", "tel", "tel_visible", "email"]
        allowed_methods = ["get", ]
        filtering = dict(
            [(key, ALL) for key in forms.SearchForm.base_fields.iterkeys()],
            level_en=ALL, level_it=ALL, level_es=ALL, level_de=ALL
        )


class FamilleResource(ModelResource):
    class Meta:
        queryset = models.Famille.objects.all()
        resource_name = "familles"
        excludes = ['user', "street", "tel", "tel_visible", "email"]
        allowed_methods = ["get", ]
        filtering = dict(
            [(key, ALL) for key in forms.FamilleSearchForm.base_fields.iterkeys()]
        )
