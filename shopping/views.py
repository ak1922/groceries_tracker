from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from .models import ShoppingTrip


@login_required
def dashboard_view(request):

    user = request.user

    if not user.family_group:
        return render(request, 'shopping/no_family_alert.html')

    all_family_trips = (
        ShoppingTrip.objects.filter(family_group=user.family_group)
        .select_related('store', 'buyer')
    )

    now = timezone.now()
    current_month_trips = all_family_trips.filter(date__year=now.year, date__month=now.month)

    total_monthly_spend = current_month_trips.aggregate(
        total=Sum('total_cost')
    )['total'] or 0.00

    context = {
        'recent_trips': all_family_trips[:10],
        'total_monthly_spend': total_monthly_spend,
        'current_month_trips_count': current_month_trips.count(),
        'family_members_count': user.family_group.members.count(),
    }

    if user.is_head():
        return render(request, 'shopping/dashboard_head.html', context)
    return render(request, 'shopping/dashboard_member.html', context)
