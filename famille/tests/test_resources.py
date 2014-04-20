from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase
from mock import Mock, MagicMock
from tastypie.exceptions import Unauthorized

from famille import resources, models
from famille.utils.auth import MessageAuthorization, UserRelatedAuthorization


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
            "auth": True
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


class AuthorizationTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user("a", "a@gmail.com", "a")
        self.famille = models.Famille(user=self.user1, email="a@gmail.com")
        self.famille.save()
        self.user2 = User.objects.create_user("b", "b@gmail.com", "b")
        self.presta = models.Prestataire(user=self.user2, description="Une description", email="b@gmail.com")
        self.presta.save()
        self.user3 = User.objects.create_user("c", "c@gmail.com", "c")
        self.presta2 = models.Prestataire(user=self.user3, description="Une description", email="c@gmail.com")
        self.presta2.save()
        self.msg1 = models.Message(sender=self.user1, subject="Toto", content="Tata")
        self.msg2 = models.Message(sender=self.user2, subject="Toto", content="Tata")
        self.msg3 = models.Message(sender=self.user3, subject="Toto", content="Tata")
        self.msg1.save()
        self.msg2.save()
        self.msg3.save()
        self.msg1.recipients.add(self.user2, self.user3)
        self.msg2.recipients.add(self.user1, self.user3)
        self.msg3.recipients.add(self.user1)

    def tearDown(self):
        User.objects.all().delete()
        models.Famille.objects.all().delete()
        models.Prestataire.objects.all().delete()
        models.Message.objects.all().delete()

    def test_has_related(self):
        auth = UserRelatedAuthorization()
        bundle = Mock(request=Mock(user=AnonymousUser()))
        self.assertRaises(Unauthorized, auth.has_related, bundle)
        bundle.request.user = self.user1
        self.assertIsNone(auth.has_related(bundle))

    def test_details_permissions(self):
        auth = MessageAuthorization()
        object_list = models.Message.objects.all()
        bundle = Mock(request=Mock(user=self.user1))
        self.assertTrue(auth.details_permission(object_list, bundle))

        object_list = object_list.filter(sender=self.user3)
        bundle.request.user = self.user2
        self.assertFalse(auth.details_permission(object_list, bundle))

    def test_list_queryset(self):
        auth = MessageAuthorization()
        object_list = models.Message.objects.all()
        bundle = Mock(request=Mock(user=self.user1))
        self.assertEqual(auth.list_queryset(object_list, bundle).count(), 3)

        bundle.request.user = self.user2
        self.assertEqual(auth.list_queryset(object_list, bundle).count(), 2)

        object_list = object_list.filter(sender=self.user3)
        bundle.request.user = self.user2
        self.assertEqual(auth.list_queryset(object_list, bundle).count(), 0)
