# -*- coding=utf-8 -*-
import base64
import collections
from datetime import datetime, timedelta, date
import json
import types

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.http.request import HttpRequest
from django.test import TestCase
from django.utils.timezone import utc
from mock import MagicMock, patch
from paypal.standard.ipn.models import PayPalIPN
from verification.models import KeyGroup, Key

from famille import models, errors
from famille.models import utils, planning
from famille.models.users import (
    UserInfo, FamilleFavorite, PrestataireFavorite,
    Geolocation, check_plan_expiration
)
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
        self._old_MIN_VISIBILITY_SCORE = settings.MIN_VISIBILITY_SCORE
        settings.MIN_VISIBILITY_SCORE = 0.9

    def tearDown(self):
        User.objects.all().delete()
        models.Famille.objects.all().delete()
        models.Prestataire.objects.all().delete()
        models.Geolocation.objects.all().delete()
        FamilleFavorite.objects.all().delete()
        PrestataireFavorite.objects.all().delete()
        self.keygroup.delete()
        settings.MIN_VISIBILITY_SCORE = self._old_MIN_VISIBILITY_SCORE

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

    def test_get_favorites_data_presta(self):
        favs = self.famille.get_favorites_data()
        self.assertIsInstance(favs, collections.OrderedDict)
        self.assertIn("Prestataire", favs)
        self.assertEqual(len(favs["Prestataire"]), 1)
        self.assertIsInstance(favs["Prestataire"][0], models.Prestataire)
        self.assertEqual(favs["Prestataire"][0].description, self.presta.description)

    def test_get_favorites_data_famille(self):
        favs = self.presta.get_favorites_data()
        self.assertIsInstance(favs, collections.OrderedDict)
        self.assertIn("Famille", favs)
        self.assertEqual(len(favs["Famille"]), 1)
        self.assertIsInstance(favs["Famille"][0], models.Famille)
        self.assertEqual(favs["Famille"][0].description, self.famille.description)

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

    def test_create_user_free_plan(self):
        user = models.UserInfo.create_user(self.user3, "famille")
        self.assertTrue(user.is_premium)
        self.assertEqual(user.plan_expires_at, models.Famille.FREE_PLAN_EXPIRATION)

        models.Famille.FREE_PLAN_LIMIT = datetime(2013, 7, 1, tzinfo=utc)
        user = models.UserInfo.create_user(self.user2, "famille")
        self.assertFalse(user.is_premium)

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

        self.assertEqual(self.famille.get_pseudo(), "a")
        self.famille.first_name = "Mick"
        self.assertEqual(self.famille.get_pseudo(), "Mick")
        self.famille.name = "Down"
        self.assertEqual(self.famille.get_pseudo(), "Mick D.")

    def test_compute_user_visibility_filters(self):
        user = AnonymousUser()
        f = models.compute_user_visibility_filters(user)
        self.assertEqual(f.children, [('visibility_global', True)])

        f = models.compute_user_visibility_filters(self.user1)
        self.assertEqual(f.children, [('visibility_global', True), ('visibility_family', True)])

        f = models.compute_user_visibility_filters(self.user2)
        self.assertEqual(f.children, [('visibility_global', True), ('visibility_prestataire', True)])

    @patch("django.core.mail.message.EmailMessage.send")
    def test_send_verification_email(self, send):
        req = HttpRequest()
        req.META = {"HTTP_HOST": "toto.com"}
        self.presta.send_verification_email(req)
        self.assertTrue(send.called)
        self.assertEqual(Key.objects.filter(claimed_by=self.presta.user, claimed=None).count(), 1)

    def test_verify_user(self):
        self.presta.verify_user(claimant=self.presta.user)
        presta = User.objects.get(pk=self.presta.user.pk)
        self.assertTrue(self.presta.user.is_active)

    def test_enfant_display_only_name(self):
        e = models.Enfant(e_name="John")
        self.assertEqual(e.display, "John")

    def test_enfant_display_no_birthday(self):
        e = models.Enfant(e_name="John", e_school="Best school in the World")
        self.assertEqual(e.display, u"John, scolarisé à Best school in the World")

    def test_enfant_display_no_school(self):
        today = datetime.now()
        bday = today - timedelta(days=360*10)
        e = models.Enfant(e_name="John", e_birthday=bday)
        self.assertEqual(e.display, "John, 9 ans")

    def test_enfant_display_all(self):
        today = datetime.now()
        bday = today - timedelta(days=360*10)
        e = models.Enfant(e_name="John", e_school="Best school in the World", e_birthday=bday)
        self.assertEqual(e.display, u"John, 9 ans, scolarisé à Best school in the World")

    def test_decode_users_ok(self):
        data = "---".join([self.famille.encoded, self.presta.encoded])
        expected = [self.famille, self.presta]
        self.assertEquals(UserInfo.decode_users(data), expected)

    def test_decode_users_notok(self):
        data = base64.urlsafe_b64encode(json.dumps({"type": "Prestataire", "pk": 118926}))
        self.assertRaises(ValueError, UserInfo.decode_users, data)

        data = "eaziouehazoenuazehazpoieybazioueh"
        self.assertRaises(ValueError, UserInfo.decode_users, data)

    @patch("django.core.mail.EmailMessage.send")
    def test_check_plan_expiration_basic(self, send):
        self.famille.plan = "basic"
        self.famille.save()
        check_plan_expiration(None, None, self.famille.user)
        f = models.Famille.objects.get(pk=self.famille.pk)
        self.assertEquals(f.plan, "basic")
        self.assertFalse(send.called)

    @patch("django.core.mail.EmailMessage.send")
    def test_check_plan_expiration_no_exp(self, send):
        self.famille.plan = "premium"
        self.famille.plan_expires_at = None
        self.famille.save()
        check_plan_expiration(None, None, self.famille.user)
        f = models.Famille.objects.get(pk=self.famille.pk)
        self.assertEquals(f.plan, "basic")
        self.assertIsNone(f.plan_expires_at)
        self.assertTrue(send.called)

    @patch("django.core.mail.EmailMessage.send")
    def test_check_plan_expiration_expired(self, send):
        self.famille.plan = "premium"
        self.famille.plan_expires_at = datetime(2000, 1, 1)
        self.famille.save()
        check_plan_expiration(None, None, self.famille.user)
        f = models.Famille.objects.get(pk=self.famille.pk)
        self.assertEquals(f.plan, "basic")
        self.assertIsNone(f.plan_expires_at)
        self.assertTrue(send.called)

    @patch("django.core.mail.EmailMessage.send")
    def test_check_plan_expiration_not_expired(self, send):
        self.famille.plan = "premium"
        self.famille.plan_expires_at = datetime(2500, 1, 1)
        self.famille.save()
        check_plan_expiration(None, None, self.famille.user)
        f = models.Famille.objects.get(pk=self.famille.pk)
        self.assertEquals(f.plan, "premium")
        self.assertEquals(f.plan_expires_at.replace(tzinfo=None), datetime(2500, 1, 1))
        self.assertFalse(send.called)

    def test_visibility_score_empty(self):
        p = models.Prestataire()
        self.assertEquals(p.visibility_score, 0)

    def test_visibility_score_not_empty(self):
        p = models.Prestataire(type="baby", name="To", first_name="Tou", street="Rue des Moines", city="Paris")
        self.assertEquals(p.visibility_score, 0.625)

    def test_visibility_score_is_enough_zero(self):
        p = models.Prestataire()
        self.assertFalse(p.visibility_score_is_enough)

    def test_visibility_score_is_not_enough(self):
        p = models.Prestataire(type="baby", name="To", first_name="Tou", street="Rue des Moines", city="Paris")
        self.assertFalse(p.visibility_score_is_enough)

    def test_visibility_score_is_enough(self):
        settings.MIN_VISIBILITY_SCORE = 0.9
        p = models.Prestataire(
            type="baby", name="To", first_name="Tou", street="Rue des Moines", city="Paris",
            postal_code="75017", birthday=datetime.now(), profile_pic="/dumbfile.txt"
        )
        self.assertTrue(p.visibility_score_is_enough)


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

        rating.a = 4
        self.assertEqual(rating.average, 1)

        rating.b = 2
        rating.c = 1
        rating.d = 3
        self.assertEqual(rating.average, 2.5)

    def test_user_nb_ratings(self):
        self.assertEqual(self.famille.nb_ratings, 0)
        models.FamilleRatings(user=self.famille).save()
        models.FamilleRatings(user=self.famille).save()
        self.assertEqual(self.famille.nb_ratings, 2)

    def test_user_rating(self):
        self.assertEqual(self.famille.total_rating, 0)
        models.FamilleRatings(
            user=self.famille, a=4, b=2,
            c=1, d=3
        ).save()
        models.FamilleRatings(
            user=self.famille, a=1, b=3,
            d=5, c=0
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
        self.famille = models.Famille(
            user=self.user1, email="a@gmail.com", city="Paris",
            type_presta="baby", animaux=True
        )
        self.famille.save()
        self.user2 = User.objects.create_user("b", "b@gmail.com", "b")
        self.presta = models.Prestataire(
            user=self.user2, description="Une description", email="b@gmail.com",
            city="Mulhouse", type="nounou", permis=True
        )
        self.presta.save()
        self.user3 = User.objects.create_user("d", "d@gmail.com", "d")
        self.presta2 = models.Prestataire(user=self.user3, description="Une description", email="d@gmail.com")

    def tearDown(self):
        models.Prestataire.objects.all().delete()
        models.Famille.objects.all().delete()

    def test_email_is_unique_no_model(self):
        self.assertFalse(utils.email_is_unique("a@gmail.com"))
        self.assertFalse(utils.email_is_unique("b@gmail.com"))
        self.assertTrue(utils.email_is_unique("c@gmail.com"))

    def test_email_is_unique_with_model(self):
        self.assertTrue(utils.email_is_unique("d@gmail.com", self.presta2))
        self.assertFalse(utils.email_is_unique("a@gmail.com", self.presta2))
        self.assertFalse(utils.email_is_unique("b@gmail.com", self.presta2))

    def test_convert_user_to_presta(self):
        new_presta = utils.convert_user(self.famille, models.Prestataire)
        self.assertTrue(new_presta.pk)
        self.assertEqual(new_presta.city, "Paris")
        self.assertEqual(new_presta.email, "a@gmail.com")
        self.assertEqual(new_presta.user, self.user1)
        self.assertEqual(new_presta.type, "baby")
        self.assertTrue(new_presta.animaux)
        self.assertIsNone(models.Famille.objects.filter(email="a@gmail.com").first())

    def test_convert_user_to_famille(self):
        new_famille = utils.convert_user(self.presta, models.Famille)
        self.assertTrue(new_famille.pk)
        self.assertEqual(new_famille.city, "Mulhouse")
        self.assertEqual(new_famille.email, "b@gmail.com")
        self.assertEqual(new_famille.user, self.user2)
        self.assertEqual(new_famille.type_presta, "nounou")
        self.assertTrue(new_famille.permis)
        self.assertIsNone(models.Prestataire.objects.filter(email="b@gmail.com").first())


class PlanningTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user("a", "a@gmail.com", "a")
        self.famille = models.Famille(user=self.user1, email="a@gmail.com")
        self.famille.save()
        self.planning = planning.FamillePlanning(famille=self.famille)
        self.planning.save()
        self.planning.start_date = datetime(year=1991, month=7, day=12)
        self.lundi = planning.Weekday(name="Lundi")
        self.mardi = planning.Weekday(name="Mardi")
        self.matin = planning.Schedule(name="Le matin")
        self.soir = planning.Schedule(name="Le soir")
        self.lundi.save()
        self.mardi.save()
        self.matin.save()
        self.soir.save()
        self.planning.weekday.add(self.lundi)
        self.planning.schedule.add(self.matin)

    def tearDown(self):
        self.planning.delete()
        self.famille.delete()
        self.user1.delete()
        self.lundi.delete()
        self.mardi.delete()
        self.matin.delete()
        self.soir.delete()

    def test_display_one_day_no_freq(self):
        expected = u"Les Lundi (le matin), ponctuellement à partir du 12/07/1991"
        self.assertEqual(self.planning.display, expected)

    def test_display_several_days_no_freq(self):
        self.planning.weekday.add(self.mardi)
        expected = u"Les Lundi, Mardi (le matin), ponctuellement à partir du 12/07/1991"
        self.assertEqual(self.planning.display, expected)

    def test_display_several_days_freq(self):
        self.planning.weekday.add(self.mardi)
        self.planning.frequency = "hebdo"
        expected = u"Les Lundi, Mardi (le matin), toutes les semaines à partir du 12/07/1991"
        self.assertEqual(self.planning.display, expected)

    def test_display_one_day_no_freq_several_hours(self):
        self.planning.schedule.add(self.soir)
        expected = u"Les Lundi (le matin, le soir), ponctuellement à partir du 12/07/1991"
        self.assertEqual(self.planning.display, expected)


class ReferenceTestCase(TestCase):

    def test_get_famille_display_no_user(self):
        r = models.Reference(name="Coco")
        self.assertEqual(r.get_famille_display(), "Coco")

    def test_get_famille_display_referenced_user(self):
        f = models.Famille(first_name="Mister", name="Toc")
        r = models.Reference(referenced_user=f)
        self.assertEqual(r.get_famille_display(), "de Mister T. (utilise notre site)")

    def test_get_dates_display_bad_conf(self):
        r = models.Reference(name="Coco")
        self.assertFalse(r.get_dates_display())

    def test_get_dates_display_current(self):
        r = models.Reference(current=True, date_from=datetime(year=2013, day=30, month=11))
        self.assertEqual(r.get_dates_display(), u"Du 30/11/2013 à aujourd'hui")

    def test_get_dates_display_no_current(self):
        r = models.Reference(
            date_from=datetime(year=2013, day=30, month=11),
            date_to=datetime(year=2100, day=30, month=11)
        )
        self.assertEqual(r.get_dates_display(), u"Du 30/11/2013 au 30/11/2100")
