from django.test import SimpleTestCase
from django.urls import NoReverseMatch, reverse


class SecurityRouteTests(SimpleTestCase):
    def test_public_admin_creation_route_is_removed(self):
        with self.assertRaises(NoReverseMatch):
            reverse("setup_admin_user")
