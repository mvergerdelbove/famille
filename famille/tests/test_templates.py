from django.test import TestCase

from famille import models
from famille.templatetags import helpers


__all__ = ["TemplateTagsTestCase", ]


class TemplateTagsTestCase(TestCase):

    def test_get_class_name(self):
        obj = models.Prestataire()
        self.assertEqual(helpers.get_class_name(obj), "Prestataire")

        obj = models.Famille()
        self.assertEqual(helpers.get_class_name(obj), "Famille")
