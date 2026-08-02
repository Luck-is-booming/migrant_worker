from django.contrib.admin import AdminSite
from django.db import DatabaseError
from django.db.models import Q


class MRNAdminSite(AdminSite):
    site_header = 'MRN Ilam Management'
    site_title = 'MRN Ilam Admin'
    index_title = 'Organization dashboard'
    index_template = "admin/index.html"
    site_url = None  # The branded header provides the public-site link.

    app_labels = {
        "counseling": 'Counseling',
        "core": 'Website and organization',
        "members": 'Members and memberships',
        "payments": 'Membership payments',
        "blog": 'News and content',
        "auth": 'Staff and access',
    }

    app_order = {
        "counseling": 10,
        "payments": 20,
        "members": 30,
        "blog": 40,
        "core": 50,
        "auth": 90,
    }

    model_labels = {
        ("core", "ContactMessage"): 'General enquiries',
        ("core", "Membership"): 'Membership applications',
        ("core", "MembershipPaymentSettings"): 'Membership payment settings',
        ("core", "ServiceCard"): 'Homepage services',
        ("core", "OfficialResource"): 'Official resources',
        ("core", "EmergencyResource"): 'Emergency contacts',
        ("core", "FrequentlyAskedQuestion"): 'Frequently asked questions',
        ("core", "TeamMember"): 'Committee and team',
        ("members", "Person"): 'People',
        ("members", "MembershipRecord"): 'Issued memberships',
        ("members", "OrganizationUnit"): 'Membership units',
        ("members", "PotentialDuplicate"): 'Duplicate reviews',
        ("members", "MembershipNumberIssue"): 'Membership number audit',
        ("members", "ImportBatch"): 'Member import history',
        ("payments", "ManualPayment"): 'Payment reviews',
        ("blog", "Article"): 'News, notices and programs',
    }

    model_order = {
        "counseling": {
            "CounselingRequest": 10,
            "CounselingCategory": 20,
        },
        "payments": {"ManualPayment": 10},
        "members": {
            "Person": 10,
            "MembershipRecord": 20,
            "PotentialDuplicate": 30,
            "MembershipCategory": 40,
            "OrganizationUnit": 50,
            "MembershipNumberIssue": 80,
            "ImportBatch": 90,
            "MembershipNumberSequence": 100,
        },
        "blog": {"Article": 10},
        "core": {
            "ContactMessage": 10,
            "OrganizationInfo": 20,
            "Membership": 30,
            "MembershipPaymentSettings": 40,
            "ServiceCard": 50,
            "TeamMember": 60,
            "OfficialResource": 70,
            "ResourceCategory": 80,
            "EmergencyResource": 90,
            "FrequentlyAskedQuestion": 100,
            "DestinationCountry": 120,
        },
        "auth": {"User": 10, "Group": 20},
    }

    def each_context(self, request):
        context = super().each_context(request)
        context["dashboard_counts"] = self._dashboard_counts(request)
        return context

    def _dashboard_counts(self, request):
        counts = {
            "new_counseling": None,
            "new_enquiries": None,
            "open_applications": None,
            "payments_to_review": None,
            "public_people": None,
            "active_memberships": None,
            "duplicate_reviews": None,
            "draft_content": None,
        }
        if not request.user.is_authenticated:
            return counts

        try:
            if request.user.has_perm("counseling.view_counselingrequest"):
                from counseling.models import CounselingRequest

                counts["new_counseling"] = CounselingRequest.objects.filter(
                    status="new"
                ).count()

            if request.user.has_perm("core.view_contactmessage"):
                from core.models import ContactMessage

                counts["new_enquiries"] = ContactMessage.objects.filter(
                    status="new"
                ).count()

            if request.user.has_perm("core.view_membership"):
                from core.models import Membership

                counts["open_applications"] = Membership.objects.filter(
                    is_approved=False, payment_status="pending"
                ).count()

            if request.user.has_perm("payments.view_manualpayment"):
                from payments.models import ManualPayment

                counts["payments_to_review"] = ManualPayment.objects.filter(
                    status__in=[
                        ManualPayment.STATUS_PENDING,
                        ManualPayment.STATUS_NEEDS_REVIEW,
                    ]
                ).count()

            if request.user.has_perm("members.view_person"):
                from members.models import Person

                counts["public_people"] = Person.objects.filter(
                    is_public=True,
                    merged_into__isnull=True,
                    memberships__is_public=True,
                    memberships__status__in=(
                        "active", "inactive", "pending", "expired", "suspended"
                    ),
                ).distinct().count()

            if request.user.has_perm("members.view_membershiprecord"):
                from members.models import MembershipRecord

                counts["active_memberships"] = MembershipRecord.objects.filter(
                    status="active"
                ).count()

            if request.user.has_perm("members.view_potentialduplicate"):
                from members.models import PotentialDuplicate

                counts["duplicate_reviews"] = PotentialDuplicate.objects.filter(
                    status="pending"
                ).count()

            if request.user.has_perm("blog.view_article"):
                from blog.models import Article

                counts["draft_content"] = Article.objects.filter(
                    Q(status="draft") | Q(status="archived")
                ).count()
        except DatabaseError:
            # Keep the admin login and dashboard available during migrations or a
            # temporary database issue. Individual admin pages will report errors
            # normally if the database remains unavailable.
            pass

        return counts

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        for app in app_list:
            label = app["app_label"]
            app["name"] = self.app_labels.get(label, app["name"])
            order = self.model_order.get(label, {})
            for model in app["models"]:
                object_name = model.get("object_name", "")
                model["name"] = self.model_labels.get(
                    (label, object_name), model["name"]
                )
            app["models"].sort(
                key=lambda model: (
                    order.get(model.get("object_name", ""), 999),
                    str(model["name"]).casefold(),
                )
            )

        app_list.sort(
            key=lambda app: (
                self.app_order.get(app["app_label"], 999),
                str(app["name"]).casefold(),
            )
        )
        return app_list
