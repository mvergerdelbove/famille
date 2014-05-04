from ajax_select import LookupChannel
from django.db.models import Q

from famille.models import Famille, Prestataire


class PostmanUserLookup(LookupChannel):

    model = Prestataire

    def get_query(self, q, request):
        # TODO: check visibility + premium
        return self.model.objects.filter(
            Q(name__icontains=q) | Q(email__istartswith=q) |
            Q(first_name__icontains=q) | Q(pseudo__istartswith=q)
        ).order_by('name')

    def get_result(self, obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.get_pseudo()
