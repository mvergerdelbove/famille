import base64
from datetime import date, datetime, timedelta
import json

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.core.signing import BadSignature
from django.http import HttpResponseBadRequest, Http404
from django.http.request import QueryDict, HttpRequest
from django.test import TestCase
from django.utils.timezone import utc
from mock import MagicMock, patch
from paypal.standard.ipn.models import PayPalIPN
from postman.models import Message

from famille import utils, models, errors
from famille.models.users import Geolocation
from famille.utils import geolocation, http, python, mail, payment, lookup


__all__ = ["UtilsTestCase", "GeolocationTestCase", "PythonTestCase", "HTTPTestCase"]


class UtilsTestCase(TestCase):

    def test_get_context(self):
        self.assertIn("site_title", utils.get_context())
        self.assertIn("site_title", utils.get_context(other="value"))
        self.assertEqual(utils.get_context(other="value")["other"], "value")

    def test_parse_resource_uri(self):
        _in = "not a uri"
        self.assertRaises(ValueError, utils.parse_resource_uri, _in)

        _in = "/api/v1/prestataires/12/"
        out = "prestataire", "12"
        self.assertEqual(utils.parse_resource_uri(_in), out)

        _in = "/api/v1/familles/123"
        out = "famille", "123"
        self.assertEqual(utils.parse_resource_uri(_in), out)

    def test_get_overlap(self):
        self.assertEqual(utils.get_overlap([1,2], [3,4]), 0)
        self.assertEqual(utils.get_overlap([1,2], [2,4]), 1)
        self.assertEqual(utils.get_overlap([1,2], [1,4]), 2)
        self.assertEqual(utils.get_overlap([1,4], [3,4]), 2)

class GeolocationTestCase(TestCase):

    def test_geodistance(self):
        origin = Geolocation(lat=12.2, lon=1.0)
        to = origin
        self.assertEqual(geolocation.geodistance(origin, to), 0)

        origin = Geolocation(lat=48.895603, lon=2.322858)  # 32 rue des epinettes
        to = Geolocation(lat=48.883588, lon=2.327195)  # place de clichy
        self.assertLessEqual(geolocation.geodistance(origin, to), 1.4)  # ~ 1.373 km

    def test_is_close_enough(self):
        origin = Geolocation(lat=12.2, lon=1.0)
        to = origin
        self.assertTrue(geolocation.is_close_enough(origin, to, 0))

        origin = Geolocation(lat=48.895603, lon=2.322858)  # 32 rue des epinettes
        to = Geolocation(lat=48.883588, lon=2.327195)  # place de clichy
        self.assertTrue(geolocation.is_close_enough(origin, to, 1.4))  # ~ 1.373 km
        self.assertFalse(geolocation.is_close_enough(origin, to, 1.3))  # ~ 1.373 km

    @patch("pygeocoder.Geocoder.geocode")
    def test_geolocate(self, mock):
        mock.return_value = []
        self.assertRaises(errors.GeolocationError, geolocation.geolocate, "")
        mock.return_value = [1]
        self.assertRaises(errors.GeolocationError, geolocation.geolocate, "")


class PythonTestCase(TestCase):

    def test_pick(self):
        _in = {"a": "ok", "b": "ko"}
        out = {"a": "ok"}
        self.assertEqual(python.pick(_in, "a", "c"), out)

        _in = QueryDict("a=1&b=2&a=3")
        out = {"a": ["1", "3"]}
        self.assertEqual(python.pick(_in, "a", "c"), out)

    def test_without(self):
        _in = {"a": "ok", "b": "ko"}
        out = {"a": "ok"}
        self.assertEqual(python.without(_in, "b", "c"), out)

    def test_repeat_lambda(self):
        out = list(python.repeat_lambda(dict, 2))
        self.assertEqual(len(out), 2)
        self.assertIsNot(out[0], out[1])

        out = list(python.repeat_lambda(dict, -10))
        self.assertEqual(len(out), 0)

    def test_isplit(self):
        _in = [1, 2, 3]
        q, r = python.isplit(_in, 2)
        q, r = list(q), list(r)
        self.assertEqual(q, [1, 2])
        self.assertEqual(r, [3])

    def test_jsonencoder(self):
        d = date.today()
        dt = datetime.now()
        data = {"date": d, "datetime": dt}
        expected  = '{"date": "%s", "datetime": "%s"}' % (d.isoformat(), dt.isoformat())
        self.assertEqual(json.dumps(data, cls=python.JSONEncoder), expected)

    def test_generate_timestamp(self):
        t = python.generate_timestamp()
        self.assertIsInstance(t, int)

    def test_get_age_from_date(self):
        self.assertIsNone(python.get_age_from_date(None))
        d = date.today() - timedelta(days=360*10)
        self.assertEquals(python.get_age_from_date(d), 9)


class HTTPTestCase(TestCase):

    def setUp(self):
        self.user = User(username="test@email.com", email="test@email.com", password="p")
        self.user.save()
        self.user_no_related = User(username="test2@email.com", email="test2@email.com", password="p")
        self.user_no_related.save()
        self.famille = models.Famille(user=self.user)
        self.famille.save()
        self.request = MagicMock(META={"CONTENT_TYPE": "text/html"}, body="my body")

    def tearDown(self):
        self.user.delete()
        self.user_no_related.delete()
        self.famille.delete()

    def test_require_json(self):
        def view(request, user):
            return "success"

        decorated = http.require_JSON(view)
        self.assertIsInstance(decorated(self.request, "user"), HttpResponseBadRequest)

        self.request.META["CONTENT_TYPE"] = "application/json"
        self.assertIsInstance(decorated(self.request, "user"), HttpResponseBadRequest)

        self.request.body = '{"some": "json"}'
        self.assertEqual(decorated(self.request, "user"), "success")

        # charset in content type
        self.request.META["CONTENT_TYPE"] = "application/json; charset=utf-8"
        self.assertEqual(decorated(self.request, "user"), "success")

    def test_require_related(self):
        def view(request):
            return "success"

        decorated = http.require_related(view)

        self.request.user = self.user_no_related
        self.assertRaises(Http404, decorated, self.request)

        self.request.user = self.user
        self.assertEqual(decorated(self.request), "success")
        self.assertEqual(self.request.related_user, self.famille)

    def test_jsonresponse(self):
        resp = http.JsonResponse({"toto": "tata"})
        self.assertEqual(resp.content, '{"toto": "tata"}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/json")

        resp = http.JsonResponse({"toto": "tata"}, status=400)
        self.assertEqual(resp.status_code, 400)


DUMMY_IPN = {
    "charset": "a",
    "custom": "a",
    "business": "a",
    "parent_txn_id": "a",
    "receiver_email": "a@a.com",
    "receiver_id": "a",
    "residence_country": "a",
    "txn_id": "a",
    "txn_type": "a",
    "verify_sign": "a",
    "address_country": "a",
    "address_city": "a",
    "address_country_code": "a",
    "address_name": "a",
    "address_state": "a",
    "address_street": "a",
    "address_status": "a",
    "address_zip": "a",
    "first_name": "a",
    "contact_phone": "a",
    "last_name": "a",
    "payer_business_name": "a",
    "payer_email": "a",
    "payer_id": "a",
    "auth_exp": "a",
    "auth_id": "a",
    "auth_status": "a",
    "invoice": "a",
    "item_name": "a",
    "item_number": payment.PREMIUM_IDS["1f"],
    "mc_currency": "USD",
    "memo": "a",
    "memo": "a",
    "option_name1": "a",
    "option_name2": "a",
    "payer_status": "a",
    "payment_status": "a",
    "payment_type": "a",
    "pending_reason": "a",
    "protection_eligibility": "a",
    "reason_code": "a",
    "shipping": 1.2,
    "settle_currency": "a",
    "shipping_method": "a",
    "transaction_entity": "a",
    "auction_buyer_id": "a",
    "payment_cycle": "a",
    "period_type": "a",
    "product_type": "a",
    "product_name": "a",
    "profile_status": "a",
    "rp_invoice_id": "a",
    "recurring_payment_id": "a",
    "period1": "a",
    "password": "a",
    "period2": "a",
    "period3": "a",
    "reattempt": "a",
    "recurring": "a",
    "subscr_id": "a",
    "username": "a",
    "case_id": "a",
    "case_type": "a",
    "receipt_id": "a",
    "currency_code": "a",
    "transaction_subject": "a",
    "ipaddress": "192.0.2.30",
    "flag_code": "a",
    "flag": False,
    "flag_info": "a",
    "response": "a",
    "query": "a",
}


class PaymentTestCase(TestCase):

    def setUp(self):
        self.ipn = PayPalIPN(**DUMMY_IPN)
        self.ipn.save()
        self.user = User(username="test@email.com", email="test@email.com", password="p")
        self.user.save()
        self.famille = models.Famille(user=self.user)
        self.famille.save()

    def tearDown(self):
        self.ipn.delete()
        self.famille.delete()
        self.user.delete()

    def test_sign_user_unsign_ok(self):
        signed_value = payment.signer.sign_user(self.famille)
        value = payment.signer.unsign(signed_value)
        expected = "f%s" % self.famille.pk
        self.assertEqual(value, expected)

    def test_sign_user_unsign_ko(self):
        signed_value = payment.signer.sign_user(self.famille)
        signed_value = signed_value[:-1]
        self.assertRaises(BadSignature, payment.signer.unsign, signed_value)

    def test_transaction_is_legit(self):
        signed_value = payment.signer.sign_user(self.famille)
        self.ipn.invoice = signed_value
        self.assertTrue(payment.signer.transaction_is_legit(self.ipn))

    def test_transaction_is_legit_wrong_item_number(self):
        self.ipn.item_number = "toto"
        self.assertFalse(payment.signer.transaction_is_legit(self.ipn))

    def test_transation_is_legit_wrong_invoice(self):
        self.ipn.invoice = "VDF_f%s:iaozhdazposujazdjqsio" % self.famille.pk
        self.assertFalse(payment.signer.transaction_is_legit(self.ipn))

    def test_user_from_ipn(self):
        self.ipn.invoice = payment.signer.sign_user(self.famille)
        f = payment.signer.user_from_ipn(self.ipn)
        self.assertEqual(f, self.famille)

    def test_user_from_ipn_no_user(self):
        famille = models.Famille()
        famille.pk = 122
        self.ipn.invoice = payment.signer.sign_user(famille)
        self.assertRaises(models.Famille.DoesNotExist, payment.signer.user_from_ipn, self.ipn)

    def test_user_from_ipn_wrong_signature(self):
        self.ipn.invoice = "VDF_f%s:iaozhdazposujazdjqsio" % self.famille.pk
        self.assertRaises(BadSignature, payment.signer.user_from_ipn, self.ipn)

    def test_premium_signup_ok(self):
        self.assertFalse(self.famille.is_premium)
        self.ipn.invoice = payment.signer.sign_user(self.famille)

        payment.signer.premium_signup(self.ipn)
        famille = models.Famille.objects.get(pk=self.famille.pk)
        self.assertTrue(famille.is_premium)
        expected_expires = datetime.now(utc) + timedelta(days=31)
        expected_expires = expected_expires.replace(hour=0, minute=0, second=0, microsecond=0)
        self.assertEqual(famille.plan_expires_at, expected_expires)
        self.assertEqual(famille.ipn, self.ipn)

    def test_compute_expires_at_invalid(self):
        self.ipn.item_number = "blah"
        self.assertRaises(ValueError, payment.compute_expires_at, self.ipn)

    def test_compute_expires_at_presta(self):
        self.ipn.item_number = payment.PREMIUM_IDS["12p"]
        expires_at = payment.compute_expires_at(self.ipn)
        expected = date.today() + timedelta(weeks=52)
        self.assertEqual(expires_at, expected)

    def test_compute_expires_at_famille(self):
        expires_at = payment.compute_expires_at(self.ipn)
        expected = date.today() + timedelta(days=31)
        self.assertEqual(expires_at, expected)


class MailTestCase(TestCase):

    def setUp(self):
        self.user = User(username="test@email.com", email="test@email.com", password="p")
        self.user.save()
        self.user_no_related = User(username="test2@email.com", email="test2@email.com", password="p")
        self.user_no_related.save()
        self.presta = models.Prestataire(user=self.user)
        self.presta.save()

    def tearDown(self):
        self.presta.delete()
        self.user_no_related.delete()
        self.user.delete()

    def test_email_moderation_no_related(self):
        m = Message(sender=self.user_no_related)
        rating, _ = mail.email_moderation(m)
        self.assertFalse(rating)

    def test_email_moderation_no_premium(self):
        m = Message(sender=self.user)
        rating, _ = mail.email_moderation(m)
        self.assertFalse(rating)

    def test_email_moderation_ok(self):
        self.presta.plan = self.presta.PLANS["premium"]
        self.presta.save()
        m = Message(sender=self.user)
        rating = mail.email_moderation(m)
        self.assertTrue(rating)

    def test_encode_recipient(self):
        expected = {"type": "Prestataire", "pk": self.presta.pk}
        self.assertEqual(json.loads(base64.urlsafe_b64decode(mail.encode_recipient(self.presta))), expected)

    def test_decode_recipient_list(self):
        data = [{"type": "Prestataire", "pk": 1}, {"type": "Famille", "pk": 2}]
        encoded = "---".join([base64.urlsafe_b64encode(json.dumps(d)) for d in data])
        self.assertEqual(mail.decode_recipient_list(encoded), data)


class LookupTestCase(TestCase):

    def setUp(self):
        self.user = User(username="test@email.com", email="test@email.com", password="p")
        self.user.save()
        self.user2 = User(username="test2@email.com", email="test2@email.com", password="p")
        self.user2.save()
        self.user_no_related = User(username="test3@email.com", email="test3@email.com", password="p")
        self.user_no_related.save()
        self.presta = models.Prestataire(user=self.user, first_name="Toto", plan=models.Prestataire.PLANS["premium"])
        self.presta.save()
        self.famille = models.Famille(user=self.user2, first_name="Toto2", plan=models.Prestataire.PLANS["premium"])
        self.famille.save()
        self.request = HttpRequest()
        self.lookup = lookup.PostmanUserLookup()

    def tearDown(self):
        self.presta.delete()
        self.famille.delete()
        self.user_no_related.delete()
        self.user.delete()
        self.user2.delete()

    def test_get_query_results(self):
        results = list(self.lookup.get_query_results("to"))
        self.assertEqual(len(results), 2)

    def test_format_result(self):
        expected = {
            "text": "Toto",
            "id": self.user.username
        }
        self.assertEqual(self.lookup.format_result(self.presta), expected)

    def test_check_auth_anonymous(self):
        self.request.user = AnonymousUser()
        self.assertFalse(self.lookup.check_auth(self.request))

    def test_check_auth_no_related(self):
        self.request.user = self.user_no_related
        self.assertFalse(self.lookup.check_auth(self.request))

    def test_check_auth_no_premium(self):
        self.request.user = self.user
        self.presta.plan = models.Prestataire.PLANS["basic"]
        self.presta.save()
        self.assertFalse(self.lookup.check_auth(self.request))

    def test_check_auth_ok(self):
        self.request.user = self.user
        self.assertTrue(self.lookup.check_auth(self.request))
