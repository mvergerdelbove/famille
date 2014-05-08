from itertools import chain

from django.db.models import Q

from famille.models import Famille, Prestataire, has_user_related, get_user_related


class PostmanUserLookup(object):

    def get_query_results(self, query):
        q_prestataire = self.get_queryset_from_model(Prestataire, query)
        q_famille = self.get_queryset_from_model(Famille, query)
        return chain(q_prestataire, q_famille)

    def format_result(self, obj):
        return {
            "text": obj.get_pseudo(),
            "id": obj.user.username
        }

    def check_auth(self, request):
        """
        Allow premium users to query.
        """
        if has_user_related(request.user):
            user = get_user_related(request.user)
            return user.is_premium
        return False

    @staticmethod
    def get_queryset_from_model(model_class, query):
        """
        Returns a filtered queryset from the model class.
        Can be Prestataire or Famille.

        :param model_class:        the model class
        """
        return model_class.objects.filter(
            plan=model_class.PLANS["premium"]  # can only send messages to premium user
        ).filter(
            Q(name__icontains=query) | Q(email__istartswith=query) |
            Q(first_name__icontains=query) | Q(pseudo__istartswith=query)
        ).order_by('name')
