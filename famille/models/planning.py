# -*- coding=utf-8 -*-
from datetime import datetime

from django.db import models

from famille.models.base import BaseModel
from famille.models.users import Famille, Prestataire


__all__ = [
    "FamillePlanning", "PrestatairePlanning", "Weekday", "Schedule"
]


class ChoicesModel(models.Model):

    class Meta:
        abstract = True

    @classmethod
    def get_choices(cls):
        """
        Return choices for a django form field.
        """
        return [
            (o.id, o.name)
            for o in cls.objects.all()
        ]


class Weekday(ChoicesModel):
    name = models.CharField(max_length=15)

    class Meta:
        app_label = 'famille'

    def __unicode__(self):
        return unicode(self.name)


class Schedule(ChoicesModel):
    name = models.CharField(max_length=30)

    class Meta:
        app_label = 'famille'

    def __unicode__(self):
        return unicode(self.name)


class BasePlanning(BaseModel):
    """
    A planning entry.
    """
    DISPLAY_TPL = u"Les %s, %s à partir du %s"
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

    @property
    def display(self):
        """
        Display the planning as a whole sentence.
        """
        days = u", ".join(day.name for day in self.weekday.all())
        freq = self.get_frequency_display().lower() if self.frequency == "hebdo" else u"ponctuellement"
        date = self.start_date.strftime("%d/%m/%Y")
        return self.DISPLAY_TPL % (days, freq, date)


class FamillePlanning(BasePlanning):
    famille = models.ForeignKey(Famille, related_name="planning")

    class Meta:
        app_label = 'famille'


class PrestatairePlanning(BasePlanning):
    prestataire = models.ForeignKey(Prestataire, related_name="planning")

    class Meta:
        app_label = 'famille'
