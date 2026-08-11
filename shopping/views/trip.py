from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, F

from shopping.models import ShoppingTrip, ShoppingItem
from shopping.forms import ShoppingItemForm, ShoppingTripForm


@login_required
def trip_detail(request, pk):

    trip = get_object_or_404(ShoppingTrip, id=pk, family_group=request.user.family_group)

    ItemFormSet = inlineformset_factory(
        ShoppingTrip,
        ShoppingItem,
        form=ShoppingItemForm,
        extra=0,
        can_delete=True
    )

    formset = ItemFormSet(request.POST or None, instance=trip)

    if request.method == 'POST' and formset.is_valid():
        formset.save()
        messages.success(request, 'Receipt inventory records updated successfully!')
        return redirect('shopping:dashboard')

    context = {
        'trip': trip,
        'formset': formset,
        'empty_form': formset.empty_form,
    }
    return render(request , 'shopping/trip_detail.html' , context)


@login_required
def trip_history(request):
    """
    Exposes full historical family records using chunks of 15 rows per page block.
    """
    all_trips = (
        ShoppingTrip.objects.filter(family_group=request.user.family_group)
        .select_related('store', 'buyer')
        .order_by('-date')
    )

    # Slice the database query into subsets of 15 records per page pass
    paginator = Paginator(all_trips, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request , 'shopping/trip_history.html' , {'page_obj': page_obj})



@login_required
def trip_edit(request, pk):

    trip = get_object_or_404(ShoppingTrip, id=pk, family_group=request.user.family_group)

    if trip.is_completed:
        messages.warning(request, '🔒 This shopping trip has been locked and finalized. It cannot be modified.')
        return redirect('shopping:dashboard')

    form = ShoppingTripForm(request.POST or None, instance=trip, prefix='trip')

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Transaction parameters for trip to {trip.store.name} updated.')
        return redirect('shopping:dashboard')

    context = {
        'trip': trip,
        'form': form
    }
    return render(request, 'shopping/trip_form.html', context)


@login_required
def trip_toggle_complete(request, pk):
    trip = get_object_or_404(ShoppingTrip, id=pk, family_group=request.user.family_group)

    trip.is_completed = not trip.is_completed
    trip.save(update_fields=['is_completed'])

    if trip.is_completed:
        messages.success(request, f'🔒 Trip to {trip.store.name} is now finalized and locked.')
    else:
        messages.info(request, f'🔓 Trip to {trip.store.name} is now finalized and locked.')
    return redirect('shopping:dashboard')


@login_required
def delete_trip(request, pk):
    trip = get_object_or_404(ShoppingTrip, id=pk, family_group=request.user.family_group)
    store_name = trip.store

    if request.method == 'POST':
        trip.delete()
        messages.success(request, f'🗑️ Shopping trip record to {store_name} has been successfully deleted.')
        return redirect('shopping:dashboard')

    return render(request, 'shopping/trip_confirm_delete.html')
