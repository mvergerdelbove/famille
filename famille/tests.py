from django.test import TestCase
from django.contrib.auth.models import User

from famille import forms, models, utils


class UtilsTestCase(TestCase):

    def test_get_context(self):
        self.assertIn("site_title", utils.get_context())
        self.assertIn("site_title", utils.get_context(other="value"))
        self.assertEqual(utils.get_context(other="value")["other"], "value")


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
        
