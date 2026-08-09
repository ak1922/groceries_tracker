from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from shopping.models import ShoppingTrip, ShoppingItem
from shopping.forms import ShoppingItemForm

@login_required
def trip_detail(request, pk):

    trip = get_object_or_404(ShoppingTrip, id=pk, family_group=request.user.family_group)

    ItemFormSet = inlineformset_factory(
        ShoppingTrip,
        ShoppingItem,
        form=ShoppingItemForm,
        extra=3,
        can_delete=True
    )

    formset = ItemFormSet(request.POST or None, instance=trip)

    if request.method == 'POST' and formset.is_valid():
        formset.save()
        messages.success(request, 'Receipt inventory records updated successfully!')
        return redirect('shopping:trip_detail')

    context = {
        'trip': trip,
        'formset': formset
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
