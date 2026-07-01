from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from .models import Member


def member_list(request):
    members = Member.objects.filter(is_public=True)

    q = request.GET.get("q", "").strip()
    membership_type = request.GET.get("type", "").strip()
    status = request.GET.get("status", "").strip()
    municipality = request.GET.get("municipality", "").strip()

    if q:
        members = members.filter(
            Q(name_ne__icontains=q)
            | Q(name_en__icontains=q)
            | Q(address__icontains=q)
            | Q(designation__icontains=q)
            | Q(membership_number__icontains=q)
        )

    if membership_type:
        members = members.filter(membership_type=membership_type)

    if status:
        members = members.filter(status=status)

    if municipality:
        members = members.filter(municipality__icontains=municipality)

    paginator = Paginator(members, 24)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "members/member_list.html", {
        "page_obj": page_obj,
        "q": q,
        "membership_type": membership_type,
        "status": status,
        "municipality": municipality,
    })