from django.db import models
from django.db.models import Sum, Avg, F


class ShoppingTripQuerySet(models.QuerySet):
    """
    Advanced analytical engine to calculate educational statistics for families.
    """
    def for_family(self, user):
        """Isolates data strictly to the logged-in family cluster."""
        return self.filter(family_group=user.family_group)

    def monthly_report(self, year, month):
        """Filters data points within a specific calendar month."""
        return self.filter(date__year=year, date__month=month)

    def total_family_investment(self):
        """Aggregates absolute spending accumulation across all logged logs."""
        return self.aggregate(total=Sum('total_cost'))['total'] or 0.00

    def category_breakdown(self):
        """
        Calculates spending metrics grouped by operational categories.
        Allows families to see exactly what percentage of their budget goes where.
        """
        return (
            self.values('items__category')
            .annotate(
                total_spent=Sum(F('items__price') * F('items__quantity')),
                average_item_cost=Avg('items__price'),
                total_items_bought=Sum('items__quantity')
            )
            .order_by('-total_spent')
        )

    def essential_vs_impulse_split(self):
        """
        Calculates the financial variance between necessity items and impulse/luxury items.
        Helps family groups analyze hidden leakages inside their shopping habits.
        """
        return (
            self.values('items__is_essential')
            .annotate(
                total_spent=Sum(F('items__price') * F('items__quantity')),
                items_count=Sum('items__quantity')
            )
        )

    def store_type_distribution(self):
        """
        Calculates expenditures grouped by store classification types.
        Exposes whether bulk-buying at Wholesale clubs saves money vs. local Supermarkets.
        """
        return (
            self.values('store__store_type')
            .annotate(
                total_spent=Sum('total_cost'),
                trips_count=models.Count('id')
            )
            .order_by('-total_spent')
        )
