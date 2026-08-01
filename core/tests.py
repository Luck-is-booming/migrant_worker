<<<<<<< HEAD
from django.test import SimpleTestCase
from django.urls import NoReverseMatch, reverse


class SecurityRouteTests(SimpleTestCase):
    def test_public_admin_creation_route_is_removed(self):
        with self.assertRaises(NoReverseMatch):
            reverse("setup_admin_user")
=======
from django.test import TestCase
from django.urls import NoReverseMatch, reverse


class SecurityRouteTests(TestCase):
    def test_public_admin_creation_route_is_removed(self):
        with self.assertRaises(NoReverseMatch):
            reverse("setup_admin_user")

    def test_health_endpoint(self):
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_custom_404_does_not_expose_debug_urlconf(self):
        response = self.client.get("/definitely-missing/")
        self.assertEqual(response.status_code, 404)
>>>>>>> 1d670fd (refactor)
