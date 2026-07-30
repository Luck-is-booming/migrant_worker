from django.core.paginator import Paginator
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import render

from .models import Member


def member_list(request):
    members = Member.objects.filter(is_public=True)

    q = request.GET.get("q", "").strip()
    membership_type = request.GET.get("type", "").strip()
    status = request.GET.get("status", "").strip()
    unit_name = request.GET.get("unit", "").strip()

    if q:
        members = members.filter(
            Q(name_ne__icontains=q)
            | Q(name_en__icontains=q)
            | Q(address__icontains=q)
            | Q(designation__icontains=q)
            | Q(membership_number__icontains=q)
            | Q(unit_name__icontains=q)
            | Q(destination_country__icontains=q)
        )

    if membership_type:
        members = members.filter(membership_type=membership_type)

    if status:
        members = members.filter(status=status)

    if unit_name:
        members = members.filter(unit_name=unit_name)

    members = members.annotate(
        level_order=Case(
            When(level="district", then=Value(1)),
            When(level="municipality", then=Value(2)),
            When(level="rural_municipality", then=Value(3)),
            When(level="ward", then=Value(4)),
            default=Value(9),
            output_field=IntegerField(),
        ),
        type_order=Case(
            When(membership_type="life", then=Value(1)),
            When(membership_type="general", then=Value(2)),
            default=Value(9),
            output_field=IntegerField(),
        ),
        number_missing=Case(
            When(membership_number_int__isnull=True, then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        ),
    ).order_by(
        "level_order",
        "unit_name",
        "type_order",
        "number_missing",
        "membership_number_int",
        "sort_order",
        "name_ne",
    )

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