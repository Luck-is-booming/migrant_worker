from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, render

from .models import MembershipCategory, MembershipRecord, OrganizationUnit, Person


PUBLIC_MEMBERSHIPS = MembershipRecord.objects.filter(
    is_public=True,
    person__is_public=True,
    person__merged_into__isnull=True,
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

    person_ids = matching_memberships.values_list("person_id", flat=True)
    people = (
        Person.objects.filter(
            pk__in=person_ids,
            is_public=True,
            merged_into__isnull=True,
        )
        .annotate(public_membership_count=Count("memberships", filter=Q(memberships__is_public=True)))
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
        .order_by("name_ne", "name_en", "pk")
        .distinct()
    )

<<<<<<< HEAD
    unit_options = list(
        Member.objects.filter(is_public=True)
        .exclude(unit_name="")
        .order_by("unit_name")
        .values_list("unit_name", flat=True)
        .distinct()
    )

    paginator = Paginator(members, 24)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "members/member_list.html", {
        "page_obj": page_obj,
        "q": q,
        "membership_type": membership_type,
        "status": status,
        "unit_name": unit_name,
        "unit_options": unit_options,
    })
=======
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
            ).distinct(),
            "status_choices": MembershipRecord.STATUS_CHOICES,
            "query_without_page": query_without_page.urlencode(),
        },
    )


def member_detail(request, public_id):
    person = get_object_or_404(
        Person.objects.filter(
            is_public=True,
            merged_into__isnull=True,
            memberships__is_public=True,
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
>>>>>>> 1d670fd (refactor)
