from django.db.models import Q
from tastypie.resources import ModelResource, ALL

from famille import models, forms
from famille.utils.python import pick, without


class PrestataireResource(ModelResource):
    class Meta:
        queryset = models.Prestataire.objects.all()
        resource_name = "prestataires"
        # TODO: refine this for prestataires
        excludes = ['user', "street", "tel", "tel_visible", "email"]
        allowed_methods = ["get", ]
        filtering = dict(
            [(key, ALL) for key in forms.PrestataireSearchForm.base_fields.iterkeys()],
            level_en=ALL, level_it=ALL, level_es=ALL, level_de=ALL
        )


class FamilleResource(ModelResource):
    # TODO: refine this
    FIELD_ACCESS_NOT_LOGGED = [
        "first_name", "name", "city", "country", "description"
    ]
    FIELD_DENIED_BASIC = ["email", "tel"]

    class Meta:
        queryset = models.Famille.objects.all()
        resource_name = "familles"
        # TODO: refine this
        fields = [
            "first_name", "name", "tel", "email", "city",
            "country", "description", "id"
        ]
        allowed_methods = ["get", ]
        filtering = dict(
            [(key, ALL) for key in forms.FamilleSearchForm.base_fields.iterkeys()]
        )

    def get_object_list(self, request):
        """
        Filter allowed object given the HTTP request.

        :param request:           the given HTTP request
        """
        filters = Q(visibility_global=True)

        if models.has_user_related(request.user):
            user = models.get_user_related(request.user)
            if isinstance(user, models.Famille):
                filters = filters & Q(visibility_family=True)
            else:
                filters = filters & Q(visibility_prestataire=True)

        return super(FamilleResource, self).get_object_list(request).filter(filters)

    def dehydrate(self, bundle):
        """
        Make sur the user does not see the fields he has no
        right to.

        :param bundle:        the bundle to trim
        """
        if not hasattr(bundle, "request") or not models.has_user_related(bundle.request.user):
            bundle.data = pick(bundle.data, *self.FIELD_ACCESS_NOT_LOGGED)
        else:
            user = models.get_user_related(bundle.request.user)
            if not user.is_premium:
                bundle.data = without(bundle.data, *self.FIELD_DENIED_BASIC)

        return bundle
