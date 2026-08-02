from django.core.paginator import Paginator
from django.db.models import Count, F, OuterRef, Prefetch, Q, Subquery
from django.shortcuts import get_object_or_404, render

from .models import MembershipCategory, MembershipRecord, OrganizationUnit, Person


PUBLIC_STATUS_CODES = ("active", "inactive", "pending", "expired", "suspended")
PUBLIC_MEMBERSHIPS = MembershipRecord.objects.filter(
    is_public=True,
    person__is_public=True,
    person__merged_into__isnull=True,
    status__in=PUBLIC_STATUS_CODES,
).select_related("category", "organization_unit")


def member_list(request):
    q = request.GET.get("q", "").strip()[:100]
    category = request.GET.get("category", "").strip()[:40]
    status = request.GET.get("status", "").strip()[:20]
    unit = request.GET.get("unit", "").strip()[:220]

    matching_memberships = PUBLIC_MEMBERSHIPS
    if category:
        matching_memberships = matching_memberships.filter(category__code=category)
    if status:
        matching_memberships = matching_memberships.filter(status=status)
    if unit:
        matching_memberships = matching_memberships.filter(organization_unit__slug=unit)
    if q:
        matching_memberships = matching_memberships.filter(
            Q(person__name_ne__icontains=q)
            | Q(person__name_en__icontains=q)
            | Q(membership_number__icontains=q)
            | Q(organization_unit__name_en__icontains=q)
            | Q(organization_unit__name_ne__icontains=q)
            | Q(designation__icontains=q)
        )

    sorting_membership = (
        matching_memberships
        .filter(person_id=OuterRef("pk"))
        .order_by(
            "organization_unit__display_order",
            "organization_unit__name_en",
            "category__display_order",
            F("membership_number_int").asc(nulls_last=True),
            "membership_number_normalized",
            "pk",
        )
    )

    person_ids = matching_memberships.values_list("person_id", flat=True)
    people = (
        Person.objects.filter(
            pk__in=person_ids,
            is_public=True,
            merged_into__isnull=True,
        )
        .annotate(
            public_membership_count=Count(
                "memberships",
                filter=(
                    Q(memberships__is_public=True)
                    & Q(memberships__status__in=PUBLIC_STATUS_CODES)
                ),
            ),
            sort_unit_order=Subquery(
                sorting_membership.values("organization_unit__display_order")[:1]
            ),
            sort_unit_name=Subquery(
                sorting_membership.values("organization_unit__name_en")[:1]
            ),
            sort_category_order=Subquery(
                sorting_membership.values("category__display_order")[:1]
            ),
            sort_membership_number=Subquery(
                sorting_membership.values("membership_number_int")[:1]
            ),
            sort_membership_text=Subquery(
                sorting_membership.values("membership_number_normalized")[:1]
            ),
        )
        .prefetch_related(
            Prefetch(
                "memberships",
                queryset=PUBLIC_MEMBERSHIPS.order_by(
                    "organization_unit__display_order",
                    "organization_unit__name_en",
                    "category__display_order",
                    "membership_number_int",
                    "membership_number_normalized",
                ),
                to_attr="public_memberships",
            )
        )
        .order_by(
            "sort_unit_order",
            "sort_unit_name",
            "sort_category_order",
            F("sort_membership_number").asc(nulls_last=True),
            "sort_membership_text",
            "name_ne",
            "name_en",
            "pk",
        )
        .distinct()
    )

    paginator = Paginator(people, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_without_page = request.GET.copy()
    query_without_page.pop("page", None)

    return render(
        request,
        "members/member_list.html",
        {
            "page_obj": page_obj,
            "result_count": paginator.count,
            "q": q,
            "selected_category": category,
            "selected_status": status,
            "selected_unit": unit,
            "categories": MembershipCategory.objects.filter(is_active=True),
            "units": OrganizationUnit.objects.filter(
                is_active=True,
                memberships__is_public=True,
                memberships__status__in=PUBLIC_STATUS_CODES,
            ).distinct(),
            "status_choices": [
                choice
                for choice in MembershipRecord.STATUS_CHOICES
                if choice[0] in PUBLIC_STATUS_CODES
            ],
            "query_without_page": query_without_page.urlencode(),
        },
    )


def member_detail(request, public_id):
    person = get_object_or_404(
        Person.objects.filter(
            is_public=True,
            merged_into__isnull=True,
            memberships__is_public=True,
            memberships__status__in=PUBLIC_STATUS_CODES,
        ).distinct().prefetch_related(
            Prefetch(
                "memberships",
                queryset=PUBLIC_MEMBERSHIPS.order_by(
                    "organization_unit__display_order",
                    "category__display_order",
                    "membership_number_int",
                ),
                to_attr="public_memberships",
            )
        ),
        public_id=public_id,
    )
    return render(request, "members/member_detail.html", {"person": person})
