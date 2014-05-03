from django.conf import settings
from django.core.exceptions import FieldError
from django.db.models import Q
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import InvalidSortError

from famille import models, forms, errors
from famille.models import planning, compute_user_visibility_filters
from famille.utils.python import pick, without
from famille.utils.geolocation import is_close_enough, geolocate


class WeekdayResource(ModelResource):
    """
    A resource representing a weekday.
    """
    class Meta:
        queryset = planning.Weekday.objects.all()
        resource_name = "weekdays"
        fields = ["name", "id"]
        allowed_methods = ["get", ]
        filtering = {
            "name": ALL,
            "id": ALL
        }


class ScheduleResource(ModelResource):
    """
    A resource representing a weekday.
    """
    class Meta:
        queryset = planning.Schedule.objects.all()
        resource_name = "schedules"
        fields = ["name", "id"]
        allowed_methods = ["get", ]
        filtering = {
            "name": ALL,
            "id": ALL
        }


class PlanningResource(ModelResource):
    """
    The base resource for plannings.
    """
    weekday = fields.ManyToManyField(WeekdayResource, "weekday", full=True)
    schedule = fields.ManyToManyField(ScheduleResource, "schedule", full=True)

    class Meta:
        fields = [
            "start_date", "weekday", "frequency", "schedule", "comment"
        ]
        allowed_methods = ["get", ]
        filtering = {
            "start_date": ALL,
            "weekday": ALL_WITH_RELATIONS,
            "frequency": ALL,
            "schedule": ALL_WITH_RELATIONS
        }


class FamillePlanningResource(PlanningResource):

    class Meta(PlanningResource.Meta):
        queryset = planning.FamillePlanning.objects.all()
        resource_name = "famille_plannings"


class PrestatairePlanningResource(PlanningResource):

    class Meta(PlanningResource.Meta):
        queryset = planning.PrestatairePlanning.objects.all()
        resource_name = "prestataire_plannings"


class EnfantResource(ModelResource):
    """
    The resource representing enfants.
    """
    school = fields.CharField(attribute="e_school")
    class Meta:
        fields = ("school", )
        queryset = models.Enfant.objects.all()
        resource_name = "enfants"
        allowed_methods = ["get", ]
        filtering = {
            "school": ALL
        }


class SearchResource(object):

    class Meta:
        allowed_methods = ["get", ]

    def apply_sorting(self, obj_list, options=None):
        """
        Override apply_sorting method to manage particular cases,
        like geolocation and rating.
        """
        order_by = options.get("order_by")

        if order_by == "-rating":
            return sorted(obj_list, key=lambda u: - u.total_rating)
        elif order_by == "geolocation":
            pass  # IDEA: dehydrate_geolocation when needed (filter / sort in request)
        else:
            return super(SearchResource, self).apply_sorting(obj_list, options)

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

    plannings = fields.ToManyField(FamillePlanningResource, "planning", full=True, null=True)
    rating = fields.FloatField(attribute="total_rating")

    class Meta(SearchResource.Meta):
        queryset = models.Prestataire.objects.all()
        resource_name = "prestataires"
        # TODO: refine this for prestataires
        excludes = ['user', "street", "tel", "tel_visible", "email"]
        ordering = [key[1:] if key.startswith("-") else key for key in forms.PrestataireSearchForm.ordering_dict.keys()]
        filtering = dict(
            [(key, ALL) for key in forms.PrestataireSearchForm.base_fields.iterkeys()],
            level_en=ALL, level_it=ALL, level_es=ALL, level_de=ALL, distance=ALL, id=ALL,
            plannings=ALL_WITH_RELATIONS, birthday=('lte','gte')
        )


class FamilleResource(SearchResource, ModelResource):
    # TODO: refine this
    FIELD_ACCESS_NOT_LOGGED = [
        "first_name", "name", "city", "country", "description"
    ]
    FIELD_DENIED_BASIC = ["email", "tel"]

    plannings = fields.ToManyField(FamillePlanningResource, "planning", full=True, null=True)
    enfants = fields.ToManyField(EnfantResource, "enfants", full=True, null=True)
    rating = fields.FloatField(attribute="total_rating")

    class Meta(SearchResource.Meta):
        queryset = models.Famille.objects.all()
        resource_name = "familles"
        # TODO: refine this
        fields = [
            "first_name", "name", "tel", "email", "city",
            "country", "description", "id", "plannings", "rating",
            "updated_at", "enfants"
        ]
        ordering = [key[1:] if key.startswith("-") else key for key in forms.FamilleSearchForm.ordering_dict.keys()]
        filtering = dict(
            [(key, ALL) for key in forms.FamilleSearchForm.base_fields.iterkeys()],
            plannings=ALL_WITH_RELATIONS, enfants=ALL_WITH_RELATIONS
        )

    def get_object_list(self, request):
        """
        Filter allowed object given the HTTP request.

        :param request:           the given HTTP request
        """
        filters = compute_user_visibility_filters(request.user)
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
