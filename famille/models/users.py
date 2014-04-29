# -*- coding=utf-8 -*-
from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from paypal.standard.ipn.signals import subscription_signup

from famille import errors
from famille.models.base import BaseModel
from famille.utils import (
    parse_resource_uri, geolocation, IMAGE_TYPES, DOCUMENT_TYPES, fields as extra_fields
)
from famille.utils.mail import send_mail_from_template_with_noreply
from famille.utils.python import pick


__all__ = [
    "Famille", "Prestataire", "Enfant",
    "get_user_related", "Reference", "UserInfo",
    "has_user_related", "user_is_located", "Geolocation",
    "compute_user_visibility_filters"
]


class Geolocation(BaseModel):
    """
    A model that represent a geolocation
    of a user.
    """
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)
    has_error = models.BooleanField(default=False)

    class Meta:
        app_label = 'famille'

    @classmethod
    def from_postal_code(cls, postal_code):
        """
        Geolocation user from postal code. This is useful
        for search using postal code.
        """
        lat, lon = geolocation.geolocate("%s France" % postal_code)  # FIXME: this will obviously only work in France
        return cls(lat=lat, lon=lon)

    def geolocate(self, address):
        """
        Geolocate a geolocation object, given an address.

        :param address:         the address to geolocate
        """
        try:
            lat, lon = geolocation.geolocate(address)
        except errors.GeolocationError:
            self.has_error = True
            self.lat = None
            self.lon = None
        else:
            self.has_error = False
            self.lat = lat
            self.lon = lon

        self.save()


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


def has_user_related(user):
    """
    Find out if a user is related to a UserInfo subclass.

    :param user:      Django user
    """
    try:
        get_user_related(user)
        return True
    except (ObjectDoesNotExist, AttributeError):
        return False


def user_is_located(user):
    """
    Find out if a user is geolocated or not.

    :param user:       Django user
    """
    if not has_user_related(user):
        return False

    related = get_user_related(user)
    return related.is_geolocated


def compute_user_visibility_filters(user):
    """
    Compute the filters that will filter the whole
    user queryset and remove the users that are not
    visible to the user passed as parameter (request.user).

    :param user:          a Django user (might be anonymous)
    """
    filters = models.Q(visibility_global=True)

    if has_user_related(user):
        user = get_user_related(user)
        if isinstance(user, Famille):
            filters &= models.Q(visibility_family=True)
        else:
            filters &= models.Q(visibility_prestataire=True)

    return filters


class UserInfo(BaseModel):
    """
    The common user info that a Famille and
    a Prestataire need.
    """
    PLANS = {
        "premium": "premium",
        "basic": "basic"
    }
    user = models.OneToOneField(User)
    geolocation = models.OneToOneField(Geolocation, blank=True, null=True)
    name = models.CharField(blank=True, max_length=50)
    first_name = models.CharField(blank=True, max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    pseudo = models.CharField(blank=True, null=True, max_length=60, unique=True)

    street = models.CharField(blank=True, null=True, max_length=100)
    postal_code = models.CharField(blank=True, null=True, max_length=8)
    city = models.CharField(blank=True, null=True, max_length=40)
    country = models.CharField(blank=True, max_length=20, default="France")
    tel = models.CharField(blank=True, null=True, max_length=15)
    tel_visible = models.BooleanField(blank=True, default=False)
    profile_pic = extra_fields.ContentTypeRestrictedFileField(
        upload_to=extra_fields.upload_to_timestamp("profile_pic"), blank=True, null=True,
        content_types=IMAGE_TYPES.values(), extensions=IMAGE_TYPES.keys(),
        max_upload_size=2621440  # 2.5MB
    )
    plan = models.CharField(blank=True, max_length=20, default="basic", choices=PLANS.items())


    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode(self.__str__())

    def __str__(self):
        return self.name

    @classmethod
    def create_user(self, dj_user, type):
        """
        Create a user from data. It distinguishes between
        Famille and Prestataire types.

        :param dj_user:      the auth.User to link to
        :param type:         the type of user
        """
        UserType = Prestataire if type == "prestataire" else Famille
        user = UserType(user=dj_user, email=dj_user.email)
        user.save()
        return user

    @staticmethod
    def premium_signup(sender, **kwargs):
        import logging

        logging.error("premium_signup: %s", sender)
        logging.error("premium_signup: %s", str(kwargs))

    @property
    def is_geolocated(self):
        """
        A property to check if a user is geolocated.
        """
        return self.geolocation and not self.geolocation.has_error

    @property
    def is_premium(self):
        """
        Return True if user is premium.
        """
        return self.plan == self.PLANS["premium"]

    @property
    def nb_ratings(self):
        """
        Return the number of total ratings the user received.
        """
        return self.ratings.all().count()

    @property
    def total_rating(self):
        """
        A property that computes the overall rating of a given user.
        """
        nb_ratings = self.nb_ratings
        if not nb_ratings:
            return 0
        return sum(rating.average for rating in self.ratings.all()) / float(nb_ratings)

    # FIXME: can be async
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
            self.country or "France"  # FIXME: this will obviously only work in France
        )

        if not self.geolocation:
            self.geolocation = Geolocation()

        self.geolocation.geolocate(address)
        self.save()

    def manage_geolocation(self, changed_data):
        """
        Manage the user geolocation. If street / postal code /
        city / country is in changed data, and if city / country
        at least is not None, the geolocation will be triggered.

        :param changed_data:        the data that changed on the model
        """
        condition = (
            any(field in changed_data for field in ("street", "postal_code", "city", "country"))
            and (self.city or self.postal_code)
        )
        if condition:
            self.geolocate()

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

    def profile_access_is_authorized(self, request):
        """
        A method to tell if a given request/user can access to
        the profile page of the user (self).

        :param request:          the request to be verified
        """
        return True

    def get_pseudo(self):
        """
        Return the pseudo of a user.
        """
        if self.pseudo:
            return self.pseudo

        pseudo = self.first_name
        if not pseudo:
            pseudo = self.email.split("@")[0]
        elif self.name:
            pseudo += " %s." % self.name[0]

        return pseudo


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
        "baby": "Baby-sitter",
        "nounou": "Nounou",
        "maternel": "Assistant(e) maternel(le)",
        "parental": "Assistant(e) parental(e)",
        "pair": "Au pair",
        "other": "Autre",
    }
    LEVEL_LANGUAGES = {
        "deb": u"Débutant",
        "mid": u"Intermédiaire",
        "pro": u"Maîtrisé",
        "bil": "Bilingue"
    }
    RESTRICTIONS = {
        "bebe": u"Bébé (0 à 1 an)",
        "jeune": u"Jeunes enfants (1 à 3 ans)",
        "marche": u"Enfants de 3 à 7 ans"
    }

    birthday = models.DateField(null=True, blank=True)
    type = models.CharField(max_length=40, choices=TYPES.items())
    other_type = models.CharField(max_length=100, null=True, blank=True)
    language_kw = dict(blank=True, null=True, max_length=10, choices=LEVEL_LANGUAGES.items())
    level_en = models.CharField(**language_kw)
    level_de = models.CharField(**language_kw)
    level_es = models.CharField(**language_kw)
    level_it = models.CharField(**language_kw)
    other_language = models.CharField(blank=True, null=True, max_length=50)
    resume = extra_fields.ContentTypeRestrictedFileField(
        upload_to=extra_fields.upload_to_timestamp("resume"), blank=True, null=True,
        content_types=DOCUMENT_TYPES.values(), extensions=DOCUMENT_TYPES.keys(),
        max_upload_size=2621440  # 2.5MB
    )
    restrictions = models.CharField(max_length=40, choices=RESTRICTIONS.items(), null=True, blank=True)

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

    # visibility
    visibility_family = models.BooleanField(default=True, blank=True)
    visibility_prestataire = models.BooleanField(default=True, blank=True)
    visibility_global = models.BooleanField(default=True, blank=True)

    class Meta:
        app_label = 'famille'

    def profile_access_is_authorized(self, request):
        """
        Athorize profile access only if request has the right to.

        :param request:            the request to be verified
        """
        if not has_user_related(request.user):
            return False

        if self.user == request.user:
            return True

        if not self.visibility_global:
            return False

        user = get_user_related(request.user)
        return self.visibility_prestataire if isinstance(user, Prestataire) else self.visibility_family


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
    TYPE_GARDE = (
        ("Domicile des parents", "Domicile des parents"),
        ("Mon domicile", "Mon domicile"),
        ("Centre/colonie", "Centre/colonie"),
        ("Maison d’assistantes parentales", "Maison d’assistantes parentales"),
        ("Autre", "Autre")
    )

    prestataire = models.ForeignKey(Prestataire, related_name="references")
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(blank=True, null=True, max_length=15)
    missions = models.TextField(blank=True, null=True)
    # FIXME: doesn't look like the proper field...
    referenced_user = models.OneToOneField(Famille, blank=True, null=True, related_name="reference_of")
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    current = models.BooleanField(blank=True, default=False)
    garde = models.CharField(blank=True, null=True, max_length=40, choices=TYPE_GARDE)

    class Meta:
        app_label = 'famille'

# consts
USER_CLASSES = {
    "Famille": Famille,
    "Prestataire": Prestataire
}

FAVORITE_CLASSES = {
    Famille: FamilleFavorite,
    Prestataire: PrestataireFavorite
}

# signals
subscription_signup.connect(UserInfo.premium_signup)
