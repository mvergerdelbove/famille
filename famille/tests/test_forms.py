from datetime import date
import re

from django.contrib.auth.models import User
from django.http.request import QueryDict
from django.test import TestCase
from mock import MagicMock, patch

from famille import forms, models
from famille.utils import fields


__all__ = ["RegistrationFormTestCase", "FamilleFormTestCase", "AccountFormManager", "FieldsTestCase"]


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
        self.assertIn("email", self.form._errors)

        self.form._errors = None
        self.form.data = {"email": "valid@email.com", "password": "p"}
        self.assertTrue(self.form.is_valid())

    @patch("famille.models.users.UserInfo.send_verification_email")
    def test_save(self, mock):
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
        self.assertFalse(model.user.is_active)

        self.form.data = {"type": "prestataire"}
        user.delete()
        self.form.save()
        model = models.Prestataire.objects.filter(email="valid@email.com").first()
        self.assertIsNotNone(model)
        self.assertIsInstance(model.user, User)
        self.assertFalse(model.user.is_active)


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


class FieldsTestCase(TestCase):

    def test_upload_to_timestamp(self):
        func = fields.upload_to_timestamp("folder")
        filename = func(None, "myfile.txt")
        self.assertTrue(filename.startswith("folder/"))
        p = re.compile("folder/\d+\.txt")
        self.assertTrue(p.match(filename))


class UserFormTestCase(TestCase):

    def setUp(self):
        class Form(forms.UserForm):
            class Meta(forms.UserForm.Meta):
                model = models.Famille

        self.user1 = User.objects.create_user("a", "a@gmail.com", "a")
        self.famille = models.Famille(user=self.user1, email="a@gmail.com")
        self.famille.save()
        self.Form = Form
        self.data = {
            "name": "Caca",
            "first_name": "Toto",
        }

    def test_is_valid_no_email(self):
        form = self.Form(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_is_valid_wrong_email(self):
        self.data["email"] = "a@gmail.com"
        form = self.Form(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_is_valid_good(self):
        self.data["email"] = "b@gmail.com"
        form = self.Form(data=self.data)
        self.assertTrue(form.is_valid())

    def test_save(self):
        self.data["email"] = "b@gmail.com"
        form = self.Form(data=self.data, instance=self.famille)
        self.assertTrue(form.is_valid())
        form.save()
        user = User.objects.get(pk=self.user1.pk)
        self.assertEqual(user.email, "b@gmail.com")
