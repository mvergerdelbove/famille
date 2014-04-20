from django.db.models import Q
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized

from famille.models import has_user_related
from famille.utils.http import require_related


class ReadOwnWriteOwnAuthorization(Authorization):
    """
    Users can only read own resources and write own
    resources.
    """

    def details_permission(self, object_list, bundle):
        raise NotImplemented()

    def list_queryset(self, object_list, bundle):
        raise NotImplemented()

    def update_list(self, object_list, bundle):
        return self.list_queryset(object_list, bundle)

    def update_detail(self, object_list, bundle):
        return self.details_permission(object_list, bundle)

    def delete_list(self, object_list, bundle):
        raise Unauthorized(json.dumps({"error": "Sorry, no deletes."}))

    def delete_detail(self, object_list, bundle):
        raise Unauthorized(json.dumps({"error": "Sorry, no deletes."}))

    def read_list(self, object_list, bundle):
        return self.list_queryset(object_list, bundle)

    def read_detail(self, object_list, bundle):
        return self.details_permission(object_list, bundle)


class UserRelatedAuthorization(Authorization):
    """
    Users can only access if they have a related user.
    """

    def has_related(self, bundle):
        if not has_user_related(bundle.request.user):
            raise Unauthorized()


class MessageAuthorization(ReadOwnWriteOwnAuthorization, UserRelatedAuthorization):
    """
    Verify that a user only reads / writes messages that are his. This class
    follows the API defined here :
    https://django-tastypie.readthedocs.org/en/latest/authorization.html#the-authorization-api
    """

    def build_Q(self, user):
        """
        Build the Q object to filter the queryset.

        :param user:        the request user
        """
        return (
            Q(sender=user) | Q(recipients=user)
        )

    def details_permission(self, object_list, bundle):
        self.has_related(bundle)
        q = self.build_Q(bundle.request.user)
        original_count = object_list.count()
        return not original_count or object_list.filter(q).distinct().count() > 0

    def list_queryset(self, object_list, bundle):
        self.has_related(bundle)
        q = self.build_Q(bundle.request.user)
        return object_list.filter(q).distinct()
