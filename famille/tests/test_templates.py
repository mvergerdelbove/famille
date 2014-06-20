from django.test import TestCase

from famille import models
from famille.templatetags import helpers, users


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

    def test_get_multi_display(self):
        self.assertEqual(users.get_multi_display(None, "language"), "--")
        self.assertEqual(users.get_multi_display("0", "language"), "Anglais")
        self.assertEqual(users.get_multi_display("0,2", "language"), "Anglais, Chinois")
        self.assertEqual(users.get_multi_display("0,829162,2", "language"), "Anglais, Chinois")

    def test_contains(self):
        self.assertTrue(helpers.contains("toto", None))
        self.assertFalse(helpers.contains(None, "toto"))
        self.assertFalse(helpers.contains("zjioze", "t"))
        self.assertTrue(helpers.contains("zjioze", "z"))

    def test_get_badge_icon_garde(self):
        obj = models.Prestataire()
        self.assertEquals(users.get_badge_icon_garde(obj, "1"), "img/badges/no-1.png")
        obj.type_garde = "1"
        self.assertEquals(users.get_badge_icon_garde(obj, "1"), "img/badges/1.png")
        obj.type_garde = "1,3,6"
        self.assertEquals(users.get_badge_icon_garde(obj, "3"), "img/badges/3.png")
