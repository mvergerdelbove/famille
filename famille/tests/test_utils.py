from datetime import date, datetime
import json

from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest, Http404
from django.http.request import QueryDict
from django.test import TestCase
from mock import MagicMock, patch

from famille import utils, models, errors
from famille.models.users import Geolocation
from famille.utils import geolocation, http, python, mail


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
