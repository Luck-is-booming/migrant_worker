from django.core.paginator import Paginator
from django.db.models import Q, IntegerField
from django.db.models.functions import Cast
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
        )

    if membership_type:
        members = members.filter(membership_type=membership_type)

    if status:
        members = members.filter(status=status)

    if unit_name:
        members = members.filter(unit_name=unit_name)

    members = members.annotate(
        member_no_int=Cast("membership_number", IntegerField())
    ).order_by(
        "unit_name",
        "member_no_int",
        "name_ne",
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
    })