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

    @property
    def average(self):
        """
        Return the average rating.
        """
        return (self.reliability + self.amability + self.serious + self.ponctuality) / 4.0


class FamilleRatings(BaseRatings):
    famille = models.ForeignKey(Famille, related_name="ratings")

    class Meta:
        app_label = 'famille'

class PrestataireRatings(BaseRatings):
    prestataire = models.ForeignKey(Prestataire, related_name="ratings")

    class Meta:
        app_label = 'famille'
