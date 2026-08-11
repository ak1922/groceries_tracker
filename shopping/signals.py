from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F
from .models import ShoppingItem, ShoppingTrip


def recalculate_trip_total(trip):
    """
    Sums up all items for a trip and updates the parent record automatically.
    """
    if not trip:
        return
    aggregates = trip.items.aggregate(
        calculated_total=Sum(F('price') * F('quantity'))
    )
    new_total = aggregates['calculated_total'] or 0.00

    ShoppingTrip.objects.filter(id=trip.id).update(total_cost=new_total)


@receiver(post_save, sender=ShoppingItem)
def update_trip_on_item_save(sender, instance, **kwargs):
    """Fires automatically whenever an item is created or edited."""
    recalculate_trip_total(instance.trip)


@receiver(post_delete, sender=ShoppingItem)
def update_trip_on_item_delete(sender, instance, **kwargs):
    """Fires automatically whenever an item is deleted."""
    recalculate_trip_total(instance.trip)
