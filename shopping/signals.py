from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ShoppingItem


def recalculate_trip_total(trip):
    """
    Sums up all items for a trip and updates the parent record automatically.
    """
    if not trip:
        return

    total = sum(item.price * item.quantity for item in trip.items.all())

    trip.total_cost = total
    trip.save(update_fields=['total_cost'])


@receiver(post_save, sender=ShoppingItem)
def update_trip_on_item_save(sender, instance, **kwargs):
    """Fires automatically whenever an item is created or edited."""
    recalculate_trip_total(instance.trip)


@receiver(post_delete, sender=ShoppingItem)
def update_trip_on_item_delete(sender, instance, **kwargs):
    """Fires automatically whenever an item is deleted."""
    recalculate_trip_total(instance.trip)
