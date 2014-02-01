# -*- coding=utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from famille.utils import geolocation


class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Geolocation(BaseModel):
    """
    A model that represent a geolocation
    of a user.
    """
    lat = models.FloatField()
    lon = models.FloatField()


def get_user_related(user):
    """
    Return the user related model. Either
    Famille or Prestataire.

    :param user:      Django user
    """
    try:
        return user.famille
    except Famille.DoesNotExist:
        return user.prestataire


class UserInfo(BaseModel):
    """
    The common user info that a Famille and
    a Prestataire need.
    """
    user = models.OneToOneField(User)
    geolocation = models.OneToOneField(Geolocation, blank=True, null=True)
    name = models.CharField(blank=True, max_length=50)
    first_name = models.CharField(blank=True, max_length=50)
    email = models.EmailField(max_length=100)

    street = models.CharField(blank=True, null=True, max_length=100)
    postal_code = models.CharField(blank=True, null=True, max_length=8)
    city = models.CharField(blank=True, null=True, max_length=40)
    country = models.CharField(blank=True, max_length=20, default="France")
    tel = models.CharField(blank=True, null=True, max_length=15)
    tel_visible = models.BooleanField(blank=True, default=False)


    class Meta:
        abstract = True

    @property
    def is_geolocated(self):
        """
        A property to check if a user is geolocated.
        """
        return bool(self.geolocation)

    def geolocate(self):
        """
        Geolocate a user, using google geolocation.
        It basically calls the Google API and
        saves the GPS coordinates into database
        """
        address = "%s %s %s, %s" % (
            self.street or "",
            self.postal_code or "",
            self.city or "",
            self.country or ""
        )
        lat, lon = geolocation.geolocate(address)
        self.geolocation = Geolocation(lat=lat, lon=lon)
        self.geolocation.save()
        self.save()


class Criteria(UserInfo):
    TYPES_GARDE = {
        "dom": "Garde à domicile",
        "part": "Garde partagée",
        "mat": "Garde par une assistante maternelle",
        "struct": "Structure d'accueil",
    }
    DIPLOMA = {
        "cap": "CAP Petite enfance",
        "deaf": u"Diplôme d'Etat Assistant(e) familial(e) (DEAF)",
        "ast": "Assistant maternel / Garde d'enfants",
        "deeje": u"Diplôme d'Etat d'éducateur de jeunes enfants (DEEJE)",
    }
    LANGUAGES = {
        "en": "Anglais",
        "de": "Allemand",
        "es": "Espagnol",
        "it": "Italien",
    }

    type_garde = models.CharField(blank=True, null=True, max_length=10, choices=TYPES_GARDE.items())
    diploma = models.CharField(blank=True, null=True, max_length=10, choices=DIPLOMA.items())
    menage = models.BooleanField(blank=True, default=False)
    repassage = models.BooleanField(blank=True, default=False)
    cdt_periscolaire = models.BooleanField(blank=True, default=False)
    sortie_ecole = models.BooleanField(blank=True, default=False)
    nuit = models.BooleanField(blank=True, default=False)
    non_fumeur = models.BooleanField(blank=True, default=False)
    devoirs = models.BooleanField(blank=True, default=False)
    urgence = models.BooleanField(blank=True, default=False)
    psc1 = models.BooleanField(blank=True, default=False)
    permis = models.BooleanField(blank=True, default=False)
    baby = models.BooleanField(blank=True, default=False)
    tarif = models.FloatField(blank=True, null=True)
    description = models.CharField(blank=True, null=True, max_length=400)

    class Meta:
        abstract = True


class Prestataire(Criteria):
    """
    The Prestataire user.
    """
    TYPES = {
        "part": "Particuliers",
        "pro": "Professionel indépendant"
    }
    LEVEL_LANGUAGES = {
        "deb": u"Débutant",
        "mid": u"Intermédiaire",
        "pro": u"Maîtrisé",
        "bil": "Bilingue"
    }

    type = models.CharField(max_length=40, choices=TYPES.items())
    sub_types = models.CharField(max_length=40) # TODO choices

    language_kw = dict(blank=True, null=True, max_length=10, choices=LEVEL_LANGUAGES.items())
    level_en = models.CharField(**language_kw)
    level_de = models.CharField(**language_kw)
    level_es = models.CharField(**language_kw)
    level_it = models.CharField(**language_kw)
    other_language = models.CharField(blank=True, null=True, max_length=50)


class Famille(Criteria):
    """
    The Famille user.
    """
    TYPE_FAMILLE = {
        "mono": "Famille monoparentale",
        "foyer": "Famille Mère/Père au foyer",
        "actif": "Famille couple actif",
    }

    type = models.CharField(blank=True, null=True, max_length=10, choices=TYPE_FAMILLE.items())
    type_presta = models.CharField(blank=True, null=True, max_length=10, choices=Prestataire.TYPES.items())
    langue = models.CharField(blank=True, max_length=10, choices=Prestataire.LANGUAGES.items())


class Enfant(BaseModel):
    """
    An child of a Famille.
    """
    famille = models.ForeignKey(Famille, related_name="enfants")
    # compelled to do this naming because we cannot change the form field names...
    e_name = models.CharField(max_length=20, db_column="name")
    e_birthday = models.DateField(blank=True, null=True, db_column="birthday")
    e_school = models.CharField(blank=True, null=True, max_length=50, db_column="school")


class BasePlanning(BaseModel):
    """
    A planning entry.
    """
    FREQUENCY = {
        "all": "Tous les jours",
        "week": "Tous les jours en semaine",
        "hebdo": "Hebdomadaire",
        "2week": "Toute les 2 semaines",
        "month": "Tous les mois"
    }
    start_date = models.DateTimeField()
    frequency = models.CharField(blank=True, null=True, max_length=10, choices=FREQUENCY.items())
    comment = models.CharField(blank=True, null=True, max_length=50)

    class Meta:
        abstract = True


class FamillePlanning(BasePlanning):
    famille = models.ForeignKey(Famille, related_name="planning")


class PrestatairePlanning(BasePlanning):
    prestataire = models.ForeignKey(Prestataire, related_name="planning")
