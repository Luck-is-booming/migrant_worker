from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from blog.models import Article
from core.models import MembershipPaymentSettings, OfficialResource, OrganizationInfo, TeamMember
from counseling.models import CounselingRequest
from members.models import MembershipRecord, OrganizationUnit, Person, PotentialDuplicate
from payments.models import ManualPayment


class Command(BaseCommand):
    help = "Report the remaining launch-readiness gaps without changing data."

    def handle(self, *args, **options):
        issues = []
        info = OrganizationInfo.objects.first()
        if not info:
            issues.append("Organization Information has not been created.")
        else:
            required = {
                "official phone": info.official_phone,
                "official email": info.official_email,
                "English office address": info.office_address_en,
                "Nepali office address": info.office_address_ne,
                "registration number": info.registration_number,
                "English registration authority": info.registration_authority_en,
                "Nepali registration authority": info.registration_authority_ne,
                "establishment date": info.established_date,
                "English service area": info.service_area_en,
                "Nepali service area": info.service_area_ne,
            }
            for label, value in required.items():
                if not str(value or "").strip():
                    issues.append(f"Missing {label} in Organization Information.")

        payment = MembershipPaymentSettings.objects.first()
        if not payment or not payment.is_ready:
            issues.append("Membership payment settings are not verified and active.")
        if not OfficialResource.objects.filter(is_active=True).exists():
            issues.append("No active official resources are published.")
        if not Article.objects.published().exists():
            issues.append("No current news, notices, programs, or awareness articles are published.")
        unknown = MembershipRecord.objects.filter(status="unknown").count()
        if unknown:
            issues.append(f"{unknown} normalized memberships still have Unknown status.")
        pending_duplicates = PotentialDuplicate.objects.filter(status="pending").count()
        if pending_duplicates:
            issues.append(f"{pending_duplicates} potential duplicate review(s) are pending.")


        incomplete_people = Person.objects.filter(is_public=True, merged_into__isnull=True).filter(
            Q(name_ne="") | Q(name_en="")
        ).count()
        if incomplete_people:
            issues.append(f"{incomplete_people} public person name(s) need bilingual review.")

        incomplete_memberships = MembershipRecord.objects.filter(is_public=True).filter(
            (Q(designation_ne="") & ~Q(designation_en=""))
            | (~Q(designation_ne="") & Q(designation_en=""))
            | (Q(destination_country_ne="") & ~Q(destination_country_en=""))
            | (~Q(destination_country_ne="") & Q(destination_country_en=""))
            | (Q(address_display_ne="") & ~Q(address_display_en=""))
            | (~Q(address_display_ne="") & Q(address_display_en=""))
        ).count()
        if incomplete_memberships:
            issues.append(
                f"{incomplete_memberships} public membership profile(s) need bilingual field review."
            )

        incomplete_team = TeamMember.objects.filter(is_active=True).filter(
            Q(name_ne="") | Q(name_en="")
            | Q(designation_ne="") | Q(designation_en="")
            | (Q(address_ne="") & ~Q(address_en=""))
            | (~Q(address_ne="") & Q(address_en=""))
        ).count()
        if incomplete_team:
            issues.append(f"{incomplete_team} active team profile(s) need bilingual review.")


        incomplete_units = OrganizationUnit.objects.filter(is_active=True).filter(
            Q(name_ne="") | Q(name_en="")
        ).count()
        if incomplete_units:
            issues.append(f"{incomplete_units} active organization unit(s) need bilingual names.")

        if settings.CLOUDINARY_URL:
            legacy_evidence = ManualPayment.objects.exclude(screenshot="").exclude(
                screenshot__startswith="authenticated/"
            ).count()
            legacy_attachments = CounselingRequest.objects.exclude(attachment="").exclude(
                attachment__startswith="authenticated/"
            ).count()
            if legacy_evidence or legacy_attachments:
                issues.append(
                    f"{legacy_evidence + legacy_attachments} legacy private upload(s) were created "
                    "before authenticated Cloudinary storage. Re-upload or remove them after review."
                )

        public_statuses = ("active", "inactive", "pending", "expired", "suspended")
        public_people = Person.objects.filter(
            is_public=True,
            merged_into__isnull=True,
            memberships__is_public=True,
            memberships__status__in=public_statuses,
        ).distinct().count()
        public_memberships = MembershipRecord.objects.filter(
            is_public=True, status__in=public_statuses
        ).count()
        self.stdout.write(f"Public people: {public_people}")
        self.stdout.write(f"Public memberships: {public_memberships}")
        if issues:
            self.stdout.write(self.style.WARNING("Launch-readiness items:"))
            for issue in issues:
                self.stdout.write(f" - {issue}")
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS("No blocking launch-readiness items were detected."))
