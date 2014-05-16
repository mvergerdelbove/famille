from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase
from mock import Mock, MagicMock

from famille import resources, models


class ResourcesTestCase(TestCase):

    def setUp(self):
        self.famille_resource = resources.FamilleResource()
        self.user1 = User.objects.create_user("a", "a@gmail.com", "a")
        self.famille = models.Famille(user=self.user1, email="a@gmail.com")
        self.famille.save()
        self.data = {
            "first_name": "John",
            "name": "Doe",
            "city": "Paris",
            "country": "France",
            "description": "A desc",
            "email": "a@gmail.com",
            "tel": "0612131415",
            "auth": True,
            "template": "toto"
        }

    def tearDown(self):
        models.Famille.objects.all().delete()
        User.objects.all().delete()

    def test_dehydrate(self):
        bundle = Mock(spec=["data"], data=self.data)
        output = self.famille_resource.dehydrate(bundle)
        self.assertEqual(set(output.data.keys()), set(resources.FamilleResource.FIELD_ACCESS_NOT_LOGGED))

        request = MagicMock(user=AnonymousUser())
        bundle = Mock(spec=["data", "request"], data=self.data, request=request)
        output = self.famille_resource.dehydrate(bundle)
        self.assertEqual(set(output.data.keys()), set(resources.FamilleResource.FIELD_ACCESS_NOT_LOGGED))

        request.user = self.user1
        bundle = Mock(spec=["data", "request"], data=self.data, request=request)
        output = self.famille_resource.dehydrate(bundle)
        self.assertEqual(set(output.data.keys()), set(resources.FamilleResource.FIELD_ACCESS_NOT_LOGGED + ["auth", ]))

        self.famille.plan = "premium"
        self.famille.save()
        bundle = Mock(spec=["data", "request"], data=self.data, request=request)
        output = self.famille_resource.dehydrate(bundle)
        self.assertEqual(output.data, self.data)