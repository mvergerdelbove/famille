from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.http.request import QueryDict
from django.test import TestCase
from mock import MagicMock, patch

from famille import forms, models, utils, signals
from famille.utils import geolocation


# disconnecting signal to not alter testing and flooding google
pre_save.disconnect(sender=models.Famille, dispatch_uid="famille_geolocate")
pre_save.disconnect(sender=models.Prestataire, dispatch_uid="prestataire_geolocate")


class UtilsTestCase(TestCase):

    def test_get_context(self):
        self.assertIn("site_title", utils.get_context())
        self.assertIn("site_title", utils.get_context(other="value"))
        self.assertEqual(utils.get_context(other="value")["other"], "value")

    def test_pick(self):
        _in = {"a": "ok", "b": "ko"}
        out = {"a": "ok"}
        self.assertEqual(utils.pick(_in, "a", "c"), out)

        _in = QueryDict("a=1&b=2&a=3")
        out = {"a": ["1", "3"]}
        self.assertEqual(utils.pick(_in, "a", "c"), out)

    def test_repeat_lambda(self):
        out = list(utils.repeat_lambda(dict, 2))
        self.assertEqual(len(out), 2)
        self.assertIsNot(out[0], out[1])

        out = list(utils.repeat_lambda(dict, -10))
        self.assertEqual(len(out), 0)

    def test_isplit(self):
        _in = [1, 2, 3]
        q, r = utils.isplit(_in, 2)
        q, r = list(q), list(r)
        self.assertEqual(q, [1, 2])
        self.assertEqual(r, [3])


class RegistrationFormTestCase(TestCase):
    def setUp(self):
        self.form = forms.RegistrationForm()
        self.user = User(username="test@email.com", email="test@email.com", password="p")
        self.user.save()

    def tearDown(self):
        self.user.delete()
        User.objects.filter(email="valid@gmail.com").delete()

    def test_is_valid(self):
        self.form.is_bound = True
        self.form.data = {"email": "test@email.com", "password": "p"}
        self.assertFalse(self.form.is_valid())

        self.form._errors = None
        self.form.data = {"email": "valid@email.com", "password": "p"}
        self.assertTrue(self.form.is_valid())

    def test_save(self):
        self.form.cleaned_data = {
            "email": "valid@email.com",
            "password": "password"
        }
        self.form.data = {"type": "famille"}

        self.form.save()
        user = User.objects.filter(email="valid@email.com").first()
        self.assertIsNotNone(user)
        model = models.Famille.objects.filter(email="valid@email.com").first()
        self.assertIsNotNone(model)
        self.assertIsInstance(model.user, User)

        self.form.data = {"type": "prestataire"}
        user.delete()
        self.form.save()
        model = models.Prestataire.objects.filter(email="valid@email.com").first()
        self.assertIsNotNone(model)
        self.assertIsInstance(model.user, User)


class FamilleFormTestCase(TestCase):

    def setUp(self):
        self.form = forms.FamilleForm()
        self.form.is_bound = True
        self.form._errors = {}
        self.user = User(username="test@email.com", email="test@email.com", password="p")
        self.user.save()
        self.famille = models.Famille(user=self.user)
        self.famille.save()
        self.enfant = models.Enfant(
            famille=self.famille, e_name="Loulou", e_birthday=date.today()
        )
        self.enfant.save()

    def tearDown(self):
        self.user.delete()
        self.famille.delete()
        models.Enfant.objects.all().delete()

    def test_unzip_data(self):
        _in = {
            "e_name": ["Tom", "Jerry"],
            "e_birthday": ["10", "11"]
        }
        out = [
            {"e_name": "Tom", "e_birthday": "10"},
            {"e_name": "Jerry", "e_birthday": "11"},
        ]
        self.assertEqual(self.form.unzip_data(_in), out)

    def test_init(self):
        # no data
        form = forms.FamilleForm(instance=self.famille)
        self.assertEqual(len(form.sub_forms), 1)

        # data : adding a child
        data = QueryDict("e_name=Loulou&e_name=Lili&e_birthday=2007-09-04&e_birthday=2003-01-20")
        form = forms.FamilleForm(data=data, instance=self.famille)
        self.assertEqual(len(form.sub_forms), 2)
        self.assertEqual(form.objs_to_delete, [])

        # data : removing children
        data = QueryDict("")
        form = forms.FamilleForm(data=data, instance=self.famille)
        self.assertEqual(form.sub_forms, [])
        self.assertEqual(len(list(form.objs_to_delete)), 1)

    def test_compute_objs_diff(self):
        def check_enfant_list(e, l):
            e = list(e)
            self.assertEqual(len(e), l)
            for ee in e:
                self.assertIs(ee.famille, self.famille)

        # adding a child
        data = [
            {"e_name": "A", "e_birthday": "2007-09-04"},
            {"e_name": "B", "e_birthday": "2003-01-12"},
        ]
        enfants = [self.enfant, ]
        enfant_list, to_delete = self.form.compute_objs_diff(data, enfants, self.famille)
        check_enfant_list(enfant_list, 2)
        self.assertEqual(list(to_delete), [])

        # removing a child
        e2 = models.Enfant(famille=self.famille, e_name="B", e_birthday=date.today())
        e2.save()
        enfants.append(e2)
        data.pop()
        enfant_list, to_delete = self.form.compute_objs_diff(data, enfants, self.famille)
        check_enfant_list(enfant_list, 1)
        to_delete = list(to_delete)
        self.assertEqual(to_delete, [e2, ])

        # removing all children
        data.pop()
        enfant_list, to_delete = self.form.compute_objs_diff(data, enfants, self.famille)
        check_enfant_list(enfant_list, 0)
        self.assertEqual(list(to_delete), enfants)

    def test_is_valid(self):
        self.form.sub_forms = [
            MagicMock(is_valid=MagicMock(return_value=True)),
            MagicMock(is_valid=MagicMock(return_value=True))
        ]
        self.assertTrue(self.form.is_valid())

        self.form.is_bound = False
        self.assertFalse(self.form.is_valid())

        self.form.is_bound = True
        self.form.sub_forms[0].is_valid.return_value = False
        self.assertFalse(self.form.is_valid())

    @patch("django.forms.models.BaseModelForm")
    def test_save(self, mock):
        self.form.sub_forms = [
            MagicMock(save=MagicMock()),
            MagicMock(save=MagicMock())
        ]
        self.form.objs_to_delete = [
            MagicMock(delete=MagicMock()),
            MagicMock(delete=MagicMock())
        ]

        out = self.form.save(commit=False)
        self.assertTrue(self.form.sub_forms[0].save.called)
        self.assertTrue(self.form.sub_forms[1].save.called)
        self.assertIsInstance(out, models.Famille)
        self.assertTrue(self.form.objs_to_delete[0].delete.called)
        self.assertTrue(self.form.objs_to_delete[1].delete.called)


class AccountFormManager(TestCase):
    def setUp(self):
        self.famille = models.Famille()
        self.prestataire = models.Prestataire()

    def test_init(self):
        # no data famille
        m = forms.AccountFormManager(instance=self.famille)
        self.assertIsNone(m.form_submitted)
        self.assertEqual(m.instance_type, "famille")
        self.assertFalse(m.is_valid())
        self.assertIsInstance(m.forms["profil"], forms.FamilleForm)

        # no data prestataire
        m = forms.AccountFormManager(instance=self.prestataire)
        self.assertEqual(m.instance_type, "prestataire")
        self.assertFalse(m.is_valid())
        self.assertIsInstance(m.forms["profil"], forms.PrestataireForm)

        # data
        data = {"submit": "attentes"}
        m = forms.AccountFormManager(instance=self.famille, data=data)
        m.forms["attentes"].is_valid = MagicMock(return_value=True)
        m.forms["profil"].is_valid = MagicMock(return_value=False)
        m.forms["attentes"].save = MagicMock()
        m.forms["profil"].save = MagicMock()

        self.assertTrue(m.is_valid())
        self.assertTrue(m.forms["attentes"].is_valid.called)
        self.assertFalse(m.forms["profil"].is_valid.called)
        m.save()
        self.assertTrue(m.forms["attentes"].save.called)
        self.assertFalse(m.forms["profil"].save.called)


class ModelsTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user("a", "a@gmail.com", "a")
        self.famille = models.Famille(user=self.user1)
        self.famille.save()
        self.user2 = User.objects.create_user("b", "b@gmail.com", "b")
        models.Prestataire(user=self.user2).save()
        self.user3 = User.objects.create_user("c", "c@gmail.com", "c")

    def tearDown(self):
        User.objects.all().delete()
        models.Famille.objects.all().delete()
        models.Prestataire.objects.all().delete()
        models.Geolocation.objects.all().delete()

    def mock_process(self, target, args, kwargs, *_, **__):
        """
        Mocking multiprocessing.Process in order to test.
        """
        def start():
            target(*args, **kwargs)
        return MagicMock(start=start)

    def test_get_user_related(self):
        self.assertIsInstance(models.get_user_related(self.user1), models.Famille)
        self.assertIsInstance(models.get_user_related(self.user2), models.Prestataire)
        self.assertRaises(ObjectDoesNotExist, models.get_user_related, self.user3)

    def test_is_geolocated(self):
        geoloc = models.Geolocation(lat=33.01, lon=2.89)
        geoloc.save()

        self.assertFalse(self.famille.is_geolocated)

        self.famille.geolocation = geoloc
        self.famille.save()
        self.assertTrue(self.famille.is_geolocated)

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

    @patch("multiprocessing.Process")
    @patch("famille.models.UserInfo.geolocate")
    def test_signal(self, mock, process):
        process.side_effect = self.mock_process
        pre_save.connect(signals.geolocate, sender=models.Famille, dispatch_uid="famille_geolocate")
        pre_save.connect(signals.geolocate, sender=models.Prestataire, dispatch_uid="prestataire_geolocate")

        self.famille.country = "France"  # not enough
        self.famille.save()
        self.assertFalse(mock.called)

        self.famille.street = "32 rue des Epinettes"  # not enough
        self.famille.save()
        self.assertFalse(mock.called)

        self.famille.city = "Paris"  # enough info to geolocate
        self.famille.save()
        self.assertTrue(mock.called)
        mock.reset_mock()

        self.famille.geolocation = models.Geolocation(lat=1.2091, lon=2.289791)  # already geolocated
        self.famille.geolocation.save()
        self.famille.save()
        self.assertFalse(mock.called)

        pre_save.disconnect(sender=models.Famille, dispatch_uid="famille_geolocate")
        pre_save.disconnect(sender=models.Prestataire, dispatch_uid="prestataire_geolocate")


class GeolocationTestCase(TestCase):

    def test_geodistance(self):
        origin = (12.2, 1.0)
        to = origin
        self.assertEqual(geolocation.geodistance(origin, to), 0)

        origin = (48.895603, 2.322858)  # 32 rue des epinettes
        to = (48.883588, 2.327195)  # place de clichy
        self.assertLessEqual(geolocation.geodistance(origin, to), 1400)  # ~ 1.373 km

    
        self.famille = models.Famille()
