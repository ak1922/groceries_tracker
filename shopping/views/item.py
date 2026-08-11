from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shopping.models import ShoppingItem


@login_required
def delete_item(request, pk):
    item = get_object_or_404(ShoppingItem, id=pk, trip__family_group=request.user.family_group)
    trip_id = item.trip.id

    if item.trip.is_completed:
        messages.warning(request, f'🔒 Cannot delete items from a locked shopping trip.')
        return redirect('shopping:dashboard')

    item_name = item.name
    item.delete()
    messages.success(request, f"🗑️ '{item_name}' removed from receipt ledger.")
    return redirect('shopping:trip_detail', pk=trip_id)
