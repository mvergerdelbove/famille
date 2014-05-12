import types

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.test import TestCase
from mock import MagicMock, patch
from paypal.standard.ipn.models import PayPalIPN
from verification.models import KeyGroup

from famille import models, errors
from famille.models import utils
from famille.models.users import UserInfo, FamilleFavorite, PrestataireFavorite, Geolocation
from famille.utils import payment


__all__ = ["ModelsTestCase", "RatingTestCase", "GeolocationTestCase"]


class ModelsTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user("a", "a@gmail.com", "a")
        self.famille = models.Famille(user=self.user1, email="a@gmail.com")
        self.famille.save()
        self.user2 = User.objects.create_user("b", "b@gmail.com", "b")
        self.presta = models.Prestataire(user=self.user2, description="Une description", email="b@gmail.com")
        self.presta.save()
        self.user3 = User.objects.create_user("c", "c@gmail.com", "c")
        self.famille_fav = FamilleFavorite(
            object_type="Prestataire", object_id=self.presta.pk, famille=self.famille
        )
        self.famille_fav.save()
        self.prestataire_fav = PrestataireFavorite(
            object_type="Famille", object_id=self.famille.pk, prestataire=self.presta
        )
        self.prestataire_fav.save()
        self.keygroup = KeyGroup(name='activate_account', generator="sha1-hex")
        self.keygroup.save()

    def tearDown(self):
        User.objects.all().delete()
        models.Famille.objects.all().delete()
        models.Prestataire.objects.all().delete()
        models.Geolocation.objects.all().delete()
        FamilleFavorite.objects.all().delete()
        PrestataireFavorite.objects.all().delete()
        self.keygroup.delete()

    def test_simple_id(self):
        self.assertEqual(self.famille.simple_id, "famille__%s" % self.famille.pk)
        self.assertEqual(self.presta.simple_id, "prestataire__%s" % self.presta.pk)

    def test_get_user_related(self):
        self.assertIsInstance(models.get_user_related(self.user1), models.Famille)
        self.assertIsInstance(models.get_user_related(self.user2), models.Prestataire)
        self.assertRaises(ObjectDoesNotExist, models.get_user_related, self.user3)

    def test_has_user_related(self):
        self.assertTrue(models.has_user_related(self.user1))
        self.assertTrue(models.has_user_related(self.user2))
        self.assertFalse(models.has_user_related(self.user3))

        anonymous = AnonymousUser()
        self.assertFalse(models.has_user_related(anonymous))

    def test_is_geolocated(self):
        geoloc = models.Geolocation(lat=33.01, lon=2.89)
        geoloc.save()

        self.assertFalse(self.famille.is_geolocated)

        self.famille.geolocation = geoloc
        self.famille.save()
        self.assertTrue(self.famille.is_geolocated)

        geoloc.has_error = True
        geoloc.save()
        self.assertFalse(self.famille.is_geolocated)

    @patch("famille.utils.geolocation.geolocate")
    def test_geolocate(self, geolocate):
        geolocate.return_value = 48.895603, 2.322858
        self.famille.street = "32 rue des Epinettes"
        self.famille.postal_code = "75017"
        self.famille.city = "Paris"
        self.famille.country = "France"
        self.famille.save()

        self.famille.geolocate()
        geolocate.assert_called_with("32 rue des Epinettes 75017 Paris, France")
        self.assertIsNotNone(models.Geolocation.objects.filter(lat=48.895603, lon=2.322858).first())
        self.assertEqual(self.famille.geolocation.lat, 48.895603)
        self.assertEqual(self.famille.geolocation.lon, 2.322858)

    @patch("famille.models.users.UserInfo.geolocate")
    def test_manage_geolocation(self, mock):
        self.famille.country = "France"  # not enough
        self.famille.save()
        self.famille.manage_geolocation(["country"])
        self.assertFalse(mock.called)

        self.famille.street = "32 rue des Epinettes"  # not enough
        self.famille.save()
        self.famille.manage_geolocation(["street"])
        self.assertFalse(mock.called)

        self.famille.city = "Paris"  # enough info to geolocate
        self.famille.save()
        self.famille.manage_geolocation(["city"])
        self.assertTrue(mock.called)
        mock.reset_mock()

        self.famille.city = ""
        self.famille.postal_code = "75017"  # enough info to geolocate
        self.famille.save()
        self.famille.manage_geolocation(["city"])
        self.assertTrue(mock.called)

    def test_add_favorite(self):
        uri = "/api/v1/prestataires/%s" % self.presta.pk
        self.famille.add_favorite(uri)
        self.assertEqual(self.famille.favorites.all().count(), 1)
        qs = FamilleFavorite.objects.filter(
            famille=self.famille, object_id=self.presta.pk, object_type="Prestataire"
        )
        self.assertEqual(qs.count(), 1)

        # cannot add same favorite
        self.famille.add_favorite(uri)
        self.assertEqual(self.famille.favorites.all().count(), 1)
        qs = FamilleFavorite.objects.filter(
            famille=self.famille, object_id=self.presta.pk, object_type="Prestataire"
        )
        self.assertEqual(qs.count(), 1)

    def test_remove_favorite(self):
        uri = "/api/v1/prestataires/%s" % self.presta.pk
        FamilleFavorite(famille=self.famille, object_id=self.presta.pk, object_type="Prestataire").save()
        self.famille.remove_favorite(uri)

        self.assertEqual(self.famille.favorites.all().count(), 0)

    def test_get_favorites_data(self):
        favs = self.famille.get_favorites_data()
        self.assertIsInstance(favs, types.GeneratorType)
        favs = list(favs)
        self.assertEqual(len(favs), 1)
        self.assertIsInstance(favs[0], models.Prestataire)
        self.assertEqual(favs[0].description, self.presta.description)

    def test_get_resource_uri(self):
        out = "/api/v1/familles/%s" % self.famille.pk
        self.assertEqual(self.famille.get_resource_uri(), out)

        out = "/api/v1/prestataires/%s" % self.presta.pk
        self.assertEqual(self.presta.get_resource_uri(), out)

    def test_get_user(self):
        self.assertEqual(self.famille_fav.get_user(), self.presta)
        self.assertEqual(self.prestataire_fav.get_user(), self.famille)

    def test_create_user(self):
        user = models.UserInfo.create_user(self.user3, "prestataire")
        self.assertIsInstance(user, models.Prestataire)
        self.assertEqual(user.email, self.user3.email)

        user.delete()
        user = models.UserInfo.create_user(self.user3, "famille")
        self.assertIsInstance(user, models.Famille)
        self.assertEqual(user.email, self.user3.email)

    def test_profile_access_is_authorized(self):
        request = MagicMock()
        self.assertTrue(self.presta.profile_access_is_authorized(request))
        # no global
        self.famille.visibility_global = False
        self.assertFalse(self.famille.profile_access_is_authorized(request))

        self.famille.visibility_global = True
        request.user = AnonymousUser()
        self.assertFalse(self.famille.profile_access_is_authorized(request))

        self.famille.visibility_prestataire = False
        request.user = self.user2
        self.assertFalse(self.famille.profile_access_is_authorized(request))
        self.famille.visibility_prestataire = True
        self.assertTrue(self.famille.profile_access_is_authorized(request))

        self.famille.visibility_family = False
        request.user = self.famille.user
        self.assertTrue(self.famille.profile_access_is_authorized(request))
        request.user = User.objects.create_user("d", "d@gmail.com", "d")
        models.Famille(user=request.user, email="d@gmail.com").save()
        self.assertFalse(self.famille.profile_access_is_authorized(request))
        self.famille.visibility_family = True
        self.assertTrue(self.famille.profile_access_is_authorized(request))

    def test_user_is_located(self):
        user = AnonymousUser()
        self.assertFalse(models.user_is_located(user))

        user = self.user1
        self.assertFalse(models.user_is_located(user))

        geoloc = models.Geolocation(lat=12.2, lon=12.2)
        geoloc.save()
        self.famille.geolocation = geoloc
        self.famille.save()
        self.assertTrue(models.user_is_located(user))

        geoloc.has_error = True
        geoloc.save()
        self.assertFalse(models.user_is_located(user))

    def test_get_pseudo(self):
        self.assertEqual(self.presta.get_pseudo(), "b")
        self.presta.first_name = "Joe"
        self.assertEqual(self.presta.get_pseudo(), "Joe")
        self.presta.name = "Jack"
        self.assertEqual(self.presta.get_pseudo(), "Joe J.")
        self.presta.pseudo = "joejoe"
        self.assertEqual(self.presta.get_pseudo(), "joejoe")

        self.assertEqual(self.famille.get_pseudo(), "a")
        self.famille.first_name = "Mick"
        self.assertEqual(self.famille.get_pseudo(), "Mick")
        self.famille.name = "Down"
        self.assertEqual(self.famille.get_pseudo(), "Mick D.")
        self.famille.pseudo = "mickey68"
        self.assertEqual(self.famille.get_pseudo(), "mickey68")

    def test_compute_user_visibility_filters(self):
        user = AnonymousUser()
        f = models.compute_user_visibility_filters(user)
        self.assertEqual(f.children, [('visibility_global', True)])

        f = models.compute_user_visibility_filters(self.user1)
        self.assertEqual(f.children, [('visibility_global', True), ('visibility_family', True)])

        f = models.compute_user_visibility_filters(self.user2)
        self.assertEqual(f.children, [('visibility_global', True), ('visibility_prestataire', True)])

    @patch("django.core.mail.send_mail")
    def test_send_verification_email(self, send_mail):
        self.presta.send_verification_email()
        self.assertTrue(send_mail.called)

    def test_verify_user(self):
        self.presta.verify_user(self.presta, claimant=self.presta)
        presta = models.Prestataire.objects.get(pk=self.presta.pk)
        self.assertTrue(presta.verified)


class GeolocationTestCase(TestCase):

    def setUp(self):
        self.geoloc = models.Geolocation()

    @patch("famille.utils.geolocation.geolocate")
    def test_from_postal_code(self, mock_geo):
        mock_geo.return_value = 12.1, 13.2
        g = models.Geolocation.from_postal_code("75001")
        self.assertIsNotNone(g)
        self.assertEqual(g.lat, 12.1)
        self.assertEqual(g.lon, 13.2)
        self.assertFalse(g.has_error)

        mock_geo.side_effect = errors.GeolocationError()
        self.assertRaises(errors.GeolocationError, models.Geolocation.from_postal_code, "75001")

    @patch("famille.utils.geolocation.geolocate")
    def test_geolocate(self, mock_geo):
        mock_geo.return_value = 12.1, 13.2
        self.geoloc.geolocate("an address")
        self.assertEqual(self.geoloc.lat, 12.1)
        self.assertEqual(self.geoloc.lon, 13.2)
        self.assertFalse(self.geoloc.has_error)
        self.assertTrue(self.geoloc.pk)

        mock_geo.side_effect = errors.GeolocationError()
        self.geoloc.geolocate("an address")
        self.assertIsNone(self.geoloc.lat)
        self.assertIsNone(self.geoloc.lon)
        self.assertTrue(self.geoloc.has_error)


class RatingTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user("a", "a@gmail.com", "a")
        self.famille = models.Famille(user=self.user1, email="a@gmail.com")
        self.famille.save()
        self.user2 = User.objects.create_user("b", "b@gmail.com", "b")
        self.presta = models.Prestataire(user=self.user2, description="Une description", email="b@gmail.com")
        self.presta.save()

    def tearDown(self):
        User.objects.all().delete()
        models.Famille.objects.all().delete()
        models.Prestataire.objects.all().delete()
        models.FamilleRatings.objects.all().delete()

    def test_average(self):
        rating = models.FamilleRatings(user=self.famille)
        self.assertEqual(rating.average, 0)

        rating.reliability = 4
        self.assertEqual(rating.average, 1)

        rating.amability = 2
        rating.serious = 1
        rating.ponctuality = 3
        self.assertEqual(rating.average, 2.5)

    def test_user_nb_ratings(self):
        self.assertEqual(self.famille.nb_ratings, 0)
        models.FamilleRatings(user=self.famille).save()
        models.FamilleRatings(user=self.famille).save()
        self.assertEqual(self.famille.nb_ratings, 2)

    def test_user_rating(self):
        self.assertEqual(self.famille.total_rating, 0)
        models.FamilleRatings(
            user=self.famille, reliability=4, amability=2,
            serious=1, ponctuality=3
        ).save()
        models.FamilleRatings(
            user=self.famille, reliability=1, amability=3,
            serious=5, ponctuality=0
        ).save()
        self.assertEqual(self.famille.total_rating, 2.375)

    def test_user_has_voted_for(self):
        models.FamilleRatings(user=self.famille, by="??").save()
        self.assertFalse(models.FamilleRatings.user_has_voted_for(self.presta, self.famille))
        models.FamilleRatings(user=self.famille, by=self.presta.simple_id).save()
        self.assertTrue(models.FamilleRatings.user_has_voted_for(self.presta, self.famille))

class UtilsTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user("a", "a@gmail.com", "a")
        self.famille = models.Famille(user=self.user1, email="a@gmail.com")
        self.famille.save()
        self.user2 = User.objects.create_user("b", "b@gmail.com", "b")
        self.presta = models.Prestataire(user=self.user2, description="Une description", email="b@gmail.com")
        self.presta.save()
        self.user3 = User.objects.create_user("d", "d@gmail.com", "d")
        self.presta2 = models.Prestataire(user=self.user3, description="Une description", email="d@gmail.com")

    def test_email_is_unique_no_model(self):
        self.assertFalse(utils.email_is_unique("a@gmail.com"))
        self.assertFalse(utils.email_is_unique("b@gmail.com"))
        self.assertTrue(utils.email_is_unique("c@gmail.com"))

    def test_email_is_unique_with_model(self):
        self.assertTrue(utils.email_is_unique("d@gmail.com", self.presta2))
        self.assertFalse(utils.email_is_unique("a@gmail.com", self.presta2))
        self.assertFalse(utils.email_is_unique("b@gmail.com", self.presta2))
