from datetime import datetime

from django.db import models

from famille.models.base import BaseModel
from famille.models.users import Famille, Prestataire


__all__ = [
    "FamillePlanning", "PrestatairePlanning"
]

class Weekday(models.Model):
    name = models.CharField(max_length=15)

    class Meta:
        app_label = 'famille'

    def __unicode__(self):
        return unicode(self.name)


class Schedule(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        app_label = 'famille'

    def __unicode__(self):
        return unicode(self.name)


class BasePlanning(BaseModel):
    """
    A planning entry.
    """
    FREQUENCY = {
        "ponct": "Ponctuel",
        "hebdo": "Toutes les semaines",
    }
    start_date = models.DateField(default=datetime.now)
    frequency = models.CharField(blank=True, null=True, max_length=10, choices=FREQUENCY.items())
    weekday = models.ManyToManyField(Weekday)
    schedule = models.ManyToManyField(Schedule)
    comment = models.CharField(blank=True, null=True, max_length=50)

    class Meta:
        abstract = True


class FamillePlanning(BasePlanning):
    famille = models.ForeignKey(Famille, related_name="planning")

    class Meta:
        app_label = 'famille'


class PrestatairePlanning(BasePlanning):
    prestataire = models.ForeignKey(Prestataire, related_name="planning")

    class Meta:
        app_label = 'famille'
