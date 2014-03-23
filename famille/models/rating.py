from django.db import models

from famille.models.base import BaseModel
from famille.models.users import Famille, Prestataire

__all__ = [
    "BaseRatings", "FamilleRatings", "PrestataireRatings"
]


class BaseRatings(BaseModel):

    reliability = models.PositiveSmallIntegerField(default=0, blank=True)
    amability = models.PositiveSmallIntegerField(default=0, blank=True)
    serious = models.PositiveSmallIntegerField(default=0, blank=True)
    ponctuality = models.PositiveSmallIntegerField(default=0, blank=True)
    by = models.CharField(max_length=50, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "by %s" % self.by

    @property
    def average(self):
        """
        Return the average rating.
        """
        return (self.reliability + self.amability + self.serious + self.ponctuality) / 4.0

    @classmethod
    def user_has_voted_for(cls, voter, user):
        """
        Returns True if a user has already voted for another one.

        :param voter:        the possible voter
        :param user:         the user that he could have voted for
        """
        return bool(cls.objects.filter(user=user, by=voter.simple_id).count())


class FamilleRatings(BaseRatings):
    user = models.ForeignKey(Famille, related_name="ratings")

    class Meta:
        app_label = 'famille'


class PrestataireRatings(BaseRatings):
    user = models.ForeignKey(Prestataire, related_name="ratings")

    class Meta:
        app_label = 'famille'
