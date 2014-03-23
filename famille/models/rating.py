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

    class Meta:
        abstract = True

    def __str__(self):
        return "by %s" % getattr(self, "by", "no one...")

    @property
    def average(self):
        """
        Return the average rating.
        """
        return (self.reliability + self.amability + self.serious + self.ponctuality) / 4.0


class FamilleRatings(BaseRatings):
    user = models.ForeignKey(Famille, related_name="ratings")
    by = models.CharField(max_length=50, null=True)

    class Meta:
        app_label = 'famille'


class PrestataireRatings(BaseRatings):
    user = models.ForeignKey(Prestataire, related_name="ratings")
    by = models.CharField(max_length=50, null=True)

    class Meta:
        app_label = 'famille'
