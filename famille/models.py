# -*- coding=utf-8 -*-
from django.contrib.auth.models import User
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


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
    # TODO : planning
    description = models.CharField(blank=True, null=True, max_length=400)
    type_garde = models.CharField(blank=True, null=True, max_length=10, choices=Criteria.TYPES_GARDE.items())
    type_presta = models.CharField(blank=True, null=True, max_length=10, choices=Prestataire.TYPES.items())
    langue = models.CharField(blank=True, max_length=10, choices=Prestataire.LANGUAGES.items())
    tarif = models.FloatField(blank=True, null=True)


class Enfant(BaseModel):
    """
    An child of a Famille.
    """
    famille = models.ForeignKey(Famille, related_name="enfants")
    # compelled to do this naming because we cannot change the form field names...
    e_name = models.CharField(max_length=20, db_column="name")
    e_birthday = models.DateField(blank=True, null=True, db_column="birthday")
    e_school = models.CharField(blank=True, null=True, max_length=50, db_column="school")
