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

    def test_get_range(self):
        self.assertEqual(helpers.get_range(""), [])
        self.assertEqual(helpers.get_range("2"), [0, 1])

    def test_subtract(self):
        self.assertEqual(helpers.substract("5", ""), 5)
        self.assertEqual(helpers.substract("5", "2"), 3)