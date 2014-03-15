# -*- coding=utf-8 -*-
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from famille.models.base import BaseModel
from famille.utils import parse_resource_uri, geolocation, fields as extra_fields
from famille.utils.mail import send_mail_from_template_with_noreply
from famille.utils.python import pick


class Geolocation(BaseModel):
    """
    A model that represent a geolocation
    of a user.
    """
    lat = models.FloatField()
    lon = models.FloatField()

    class Meta:
        app_label = 'famille'

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

    def __unicode__(self):
        return unicode(self.__str__())

    def __str__(self):
        return self.name

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
        saves the GPS coordinates into database.

        NB: since geolocate is called in a pre_save signal,
            we do not save the model to save time, since
            it'll be saved soon enough.
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

    @staticmethod
    def _geolocate(sender, instance, **kwargs):
        """
        A signal receiver to geolocate a user whenever its
        data is saved.
        """
        if not instance.geolocation and any((instance.postal_code, instance.city)):
            instance.geolocate()

    def add_favorite(self, resource_uri):
        """
        Favorite an object for the user.

        :param resource_uri:          the URI of the resource to favorite
        """
        object_type, object_id = parse_resource_uri(resource_uri)
        self.favorites.get_or_create(object_type=object_type.title(), object_id=int(object_id))

    def remove_favorite(self, resource_uri):
        """
        Unfavorite an object for the user.

        :param resource_uri:      the URI of the resource to unfavorite
        """
        object_type, object_id = parse_resource_uri(resource_uri)
        object_type = object_type.title()
        object_id = int(object_id)
        self.favorites.filter(object_type=object_type, object_id=object_id).delete()

    def get_favorites_data(self):
        """
        Retrieve the favorites data.
        """
        # FIXME: can become greedy in the future
        return (favorite.get_user() for favorite in self.favorites.all())

    # FIXME: nothing to do here...
    def get_resource_uri(self):
        """
        Return the API uri of the objet. Don't really like it but for now
        didn't find another way.
        """
        return "/api/v1/%ss/%s" % (self.__class__.__name__.lower(), self.pk)

    # FIXME: cannot test it, cannot mock...
    def send_mail_to_favorites(self, message, favorites):
        favs_to_contact = map(lambda fav: pick(fav, "object_type", "object_id"), favorites)
        favs = self.favorites.all()
        favs = (fav for fav in favs if {"object_type": fav.object_type, "object_id": str(fav.object_id)} in favs_to_contact)

        # get emails
        emails = (fav.get_user().email for fav in favs)
        # remove possible None
        emails = filter(None, emails)

        if emails:
            send_mail_from_template_with_noreply(
                "email/contact_favorites.html", message,
                subject=message.get("subject", ""), recipient_list=emails
            )


class Criteria(UserInfo):
    TYPES_GARDE_FAMILLE = {
        "dom": "Garde à domicile",
        "part": "Garde partagée",
    }
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
    RESUME_TYPES = {
        ".doc": "application/msword",
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".pages": "application/x-iwork-pages-sffpages"
    }

    type = models.CharField(max_length=40, choices=TYPES.items())
    sub_types = models.CharField(max_length=40) # TODO choices

    language_kw = dict(blank=True, null=True, max_length=10, choices=LEVEL_LANGUAGES.items())
    level_en = models.CharField(**language_kw)
    level_de = models.CharField(**language_kw)
    level_es = models.CharField(**language_kw)
    level_it = models.CharField(**language_kw)
    other_language = models.CharField(blank=True, null=True, max_length=50)
    resume = extra_fields.ContentTypeRestrictedFileField(
        upload_to="resume", blank=True, null=True,
        content_types=RESUME_TYPES.values(), extensions=RESUME_TYPES.keys(),
        max_upload_size=2621440  # 2.5MB
    )

    class Meta:
        app_label = 'famille'

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

    class Meta:
        app_label = 'famille'


class Enfant(BaseModel):
    """
    An child of a Famille.
    """
    famille = models.ForeignKey(Famille, related_name="enfants")
    # compelled to do this naming because we cannot change the form field names...
    e_name = models.CharField(max_length=20, db_column="name")
    e_birthday = models.DateField(blank=True, null=True, db_column="birthday")
    e_school = models.CharField(blank=True, null=True, max_length=50, db_column="school")

    class Meta:
        app_label = 'famille'


class BaseFavorite(BaseModel):
    """
    A model reprensenting a favorite.
    """
    OBJECT_TYPES = {
        'Prestataire': 'Prestataire',
        'Famille': 'Famille',
    }
    object_id = models.IntegerField()
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES.items())

    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode(self.__str__())

    def __str__(self):
        return "%s %s" % (self.object_type, self.object_id)

    def get_user(self):
        """
        Return the user instance that is defined by the favorite.
        """
        return USER_CLASSES[self.object_type].objects.get(pk=self.object_id)


class FamilleFavorite(BaseFavorite):
    famille = models.ForeignKey(Famille, related_name="favorites")

    class Meta:
        app_label = 'famille'

    @property
    def owner(self):
        return self.famille


class PrestataireFavorite(BaseFavorite):
    prestataire = models.ForeignKey(Prestataire, related_name="favorites")

    class Meta:
        app_label = 'famille'

    @property
    def owner(self):
        return self.prestataire


class Reference(BaseModel):
    """
    A model representing a reference for a prestataire.
    """
    prestataire = models.ForeignKey(Prestataire, related_name="references")
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(blank=True, null=True, max_length=15)
    missions = models.TextField(blank=True, null=True)
    referenced_user = models.OneToOneField(Famille, blank=True, null=True, related_name="reference_of")

    class Meta:
        app_label = 'famille'


# signals
models.signals.pre_save.connect(UserInfo._geolocate, sender=Famille, dispatch_uid="famille_geolocate")
models.signals.pre_save.connect(UserInfo._geolocate, sender=Prestataire, dispatch_uid="prestataire_geolocate")

# consts
USER_CLASSES = {
    "Famille": Famille,
    "Prestataire": Prestataire
}

FAVORITE_CLASSES = {
    Famille: FamilleFavorite,
    Prestataire: PrestataireFavorite
}