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


from django.core.management import call_command
from django.utils import translation

from core.models import FrequentlyAskedQuestion, MembershipPaymentSettings, OfficialResource


class PublicInformationRouteTests(TestCase):
    def test_root_redirect_is_permanent_and_stable(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/en/")

    def test_new_public_information_pages_exist_in_both_languages(self):
        for language in ("en", "ne"):
            with translation.override(language):
                for route_name in (
                    "membership_information",
                    "programs",
                    "privacy",
                    "disclaimer",
                ):
                    response = self.client.get(reverse(route_name))
                    self.assertEqual(response.status_code, 200, route_name)

    def test_membership_application_is_paused_until_verified_payment_details_exist(self):
        with translation.override("en"):
            response = self.client.get(reverse("membership_apply"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["payment_ready"])
        self.assertContains(response, "temporarily paused")


class PaymentSettingsTests(TestCase):
    def test_configuration_is_singleton_and_disabled_by_default(self):
        first = MembershipPaymentSettings.objects.create()
        second = MembershipPaymentSettings.objects.create(recipient_name="Updated")
        self.assertEqual(MembershipPaymentSettings.objects.count(), 1)
        self.assertEqual(first.pk, second.pk)
        second.refresh_from_db()
        self.assertEqual(second.recipient_name, "Updated")
        self.assertFalse(second.is_ready)


class LaunchContentCommandTests(TestCase):
    def test_seed_launch_content_is_idempotent(self):
        call_command("seed_launch_content", verbosity=0)
        initial = (OfficialResource.objects.count(), FrequentlyAskedQuestion.objects.count())
        call_command("seed_launch_content", verbosity=0)
        self.assertEqual(
            (OfficialResource.objects.count(), FrequentlyAskedQuestion.objects.count()),
            initial,
        )
        self.assertGreaterEqual(initial[0], 5)
        self.assertGreaterEqual(initial[1], 4)


from core.models import TeamMember


class CommitteeImportCommandTests(TestCase):
    def test_dry_run_changes_nothing_and_real_import_is_idempotent(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as directory:
            report = str(Path(directory) / "committee.csv")
            call_command(
                "import_district_executive_committee",
                dry_run=True,
                report=report,
                verbosity=0,
            )
            self.assertEqual(TeamMember.objects.count(), 0)
            call_command(
                "import_district_executive_committee",
                report=report,
                verbosity=0,
            )
            self.assertEqual(TeamMember.objects.count(), 11)
            Path(report).unlink()
            call_command(
                "import_district_executive_committee",
                report=report,
                verbosity=0,
            )
            self.assertEqual(TeamMember.objects.count(), 11)

from django.test import override_settings

from core.storage import AuthenticatedCloudinaryStorage, get_private_media_storage


class PrivateMediaStorageTests(TestCase):
    def test_authenticated_storage_metadata_round_trip(self):
        name = AuthenticatedCloudinaryStorage._pack(
            public_id="private/payment_proofs/example",
            resource_type="image",
            format_name="png",
        )
        self.assertTrue(AuthenticatedCloudinaryStorage.is_authenticated_name(name))
        self.assertEqual(
            AuthenticatedCloudinaryStorage._unpack(name),
            ("private/payment_proofs/example", "image", "png"),
        )

    @override_settings(
        CLOUDINARY_URL="cloudinary://key:secret@example",
        IS_TESTING=False,
    )
    def test_cloudinary_uses_authenticated_storage_for_private_files(self):
        self.assertIsInstance(get_private_media_storage(), AuthenticatedCloudinaryStorage)


class ResourceLanguageIsolationTests(TestCase):
    def setUp(self):
        from core.models import ResourceCategory

        self.category = ResourceCategory.objects.create(
            name_ne="आधिकारिक स्रोत",
            name_en="Official source",
            slug="language-test",
        )
        OfficialResource.objects.create(
            category=self.category,
            title_en="English-only resource",
            url="https://example.com/en",
            language="en",
        )
        OfficialResource.objects.create(
            category=self.category,
            title_ne="नेपाली स्रोत",
            url="https://example.com/ne",
            language="ne",
        )

    def test_resource_page_does_not_mix_language_specific_entries(self):
        with translation.override("en"):
            english = self.client.get(reverse("resources"))
        self.assertContains(english, "English-only resource")
        self.assertNotContains(english, "नेपाली स्रोत")

        with translation.override("ne"):
            nepali = self.client.get(reverse("resources"))
        self.assertContains(nepali, "नेपाली स्रोत")
        self.assertNotContains(nepali, "English-only resource")
