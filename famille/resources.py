from django.conf import settings
from django.db.models import Q
from tastypie.resources import ModelResource, ALL

from famille import models, forms, errors
from famille.utils.python import pick, without
from famille.utils.geolocation import is_close_enough, geolocate


class SearchResource(object):

    def apply_filters(self, request, applicable_filters):
        distance = request.GET.get("distance__iexact")
        postal_code = request.GET.get("pc__iexact")
        qs = super(SearchResource, self).apply_filters(request, applicable_filters)

        if postal_code:
            return self.filter_postal_code(postal_code, qs)

        if not distance or not models.user_is_located(request.user):
            return qs

        related = models.get_user_related(request.user)
        return self.filter_distance(distance, related.geolocation, qs)


    def filter_distance(self, distance, geoloc, queryset):
        """
        Filter the queryset using distance and the user that is querying.

        :param distance:        the distance to look for
        :param geoloc:          the user geolocation that does the query
        :param queryset:        the queryset
        """
        distance = float(distance)  # distance in km
        condition = lambda o: not o.is_geolocated or is_close_enough(geoloc, o.geolocation, distance)
        return [o for o in queryset if condition(o)]


    def filter_postal_code(self, postal_code, queryset):
        """
        Fitler the queryset using a postal code. It will geolocate the postal code
        and call filter_distance. If it fails to geolocate the postal code, it will
        return the queryset unchanged.

        :param postal_code:        the postal code to geolocate
        :param queryset:           the queryset
        """
        try:
            geoloc = models.Geolocation.from_postal_code(postal_code)
        except errors.GeolocationError:
            return queryset

        return self.filter_distance(settings.POSTAL_CODE_DISTANCE, geoloc, queryset)


class PrestataireResource(SearchResource, ModelResource):
    class Meta:
        queryset = models.Prestataire.objects.all()
        resource_name = "prestataires"
        # TODO: refine this for prestataires
        excludes = ['user', "street", "tel", "tel_visible", "email"]
        allowed_methods = ["get", ]
        filtering = dict(
            [(key, ALL) for key in forms.PrestataireSearchForm.base_fields.iterkeys()],
            level_en=ALL, level_it=ALL, level_es=ALL, level_de=ALL, distance=ALL, id=ALL
        )


class FamilleResource(SearchResource, ModelResource):
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
