from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from django.core.paginator import Paginator

from shopping.models import ShoppingTrip, ShoppingItem
from shopping.forms import StoreCreateForm, ShoppingTripForm, ShoppingItemForm

@login_required
def dashboard_view(request):

    user = request.user

    if not user.family_group:
        return render(request , 'shopping/no_family_alert.html')

    all_family_trips = (
        ShoppingTrip.objects.filter(family_group=user.family_group)
        .select_related('store', 'buyer')
        .order_by('-date')
    )

    now = timezone.now()
    current_month_trips = all_family_trips.filter(date__year=now.year, date__month=now.month)

    total_monthly_spend = current_month_trips.aggregate(
        total=Sum('total_cost')
    )['total'] or 0.00

    # Forms
    trip_form = ShoppingTripForm(request.POST or None, prefix='trip')
    store_form = StoreCreateForm(request.POST or None, prefix='store')

    if request.method == 'POST':
        if 'submit_store' in request.POST:
            if store_form.is_valid():
                store_form.save()
                messages.success(request, "New vendor store added to household directory!")
                return redirect('shopping:dashboard')
            else:
                messages.error(request, f"Failed to add store. {store_form.errors.as_text()}")

        elif 'submit_trip' in request.POST:
            if trip_form.is_valid():
                trip = trip_form.save(commit=False)
                trip.buyer = user
                trip.family_group = user.family_group
                trip.save()
                messages.success(request, f"Trip to {trip.store.name} recorded! Click its name link to append items.")
                return redirect('shopping:dashboard')
            else:
                for field, errors in trip_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Trip Form Error: {error}")

    context = {
        'recent_trips': all_family_trips[:10],
        'total_monthly_spend': total_monthly_spend,
        'current_month_trips_count': current_month_trips.count(),
        'family_members_count': user.family_group.members.count(),
        'store_form': store_form,
        'trip_form': trip_form,
    }

    if user.is_head():
        return render(request , 'shopping/dashboard_head.html' , context)
    return render(request , 'shopping/dashboard_member.html' , context)
