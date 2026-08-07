from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, Avg


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

        # We query the related ShoppingItem table across the current trip queryset
        return (
            self.values('items__category')
            .annotate(
                total_spent=Sum(models.F('items__price') * models.F('items__quantity')),
                average_item_cost=Avg('items__price'),
                total_items_bought=Sum('items__quantity')
            )
            .order_by('-total_spent')
        )


class Store(models.Model):
    name= models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class ShoppingTrip(models.Model):
    family_group = models.ForeignKey('users.FamilyGroup', on_delete=models.CASCADE, related_name='trips')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='trips_logged')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='trips')
    date = models.DateField(default=timezone.now)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_completed = models.BooleanField(default=False)

    objects = ShoppingTripQuerySet.as_manager()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.store.name} - {self.date}'




class ShoppingItem(models.Model):
    """
    Detailed product definitions paired with custom unit tracking metrics.
    """
    class ProductCategories(models.TextChoices):
        PRODUCE = 'VEG', 'Fruits & Vegetables 🍎'
        DAIRY_EGGS = 'DRY', 'Dairy, Milk & Eggs 🥛'
        MEAT_SEAFOOD = 'PRO', 'Meat, Poultry & Fish 🥩'
        BAKERY = 'BAK', 'Bakery & Bread 🍞'
        PANTRY = 'PAN', 'Pantry & Dry Goods 🌾'
        SNACKS_SWEETS = 'JNK', 'Snacks & Treats 🍫'
        BEVERAGES = 'BEV', 'Beverages & Drinks 🥤'
        HOUSEHOLD = 'HSH', 'Household & Cleaning 🧼'

    class UnitTypes(models.TextChoices):
        PIECE = 'PCS', 'Count / Per Item'
        POUND = 'LBS', 'Pound (lbs)'
        OUNCE = 'OZ', 'Ounce (oz)'
        GALLON = 'GAL', 'Gallon'

    trip = models.ForeignKey(ShoppingTrip, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=150)
    category = models.CharField(
        max_length=3,
        choices=ProductCategories.choices,
        default=ProductCategories.PANTRY
    )

    # Financial parameters
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Price per single unit container")

    # Educational Unit Metric Fields
    unit_type = models.CharField(max_length=3, choices=UnitTypes.choices, default=UnitTypes.PIECE)
    unit_size = models.DecimalField(max_digits=6, decimal_places=2, default=1.00, help_text="e.g., enter 16.00 for a 16oz cereal box")

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    @property
    def cost_per_unit_measurement(self):
        """
        Calculates the real unit price (e.g., price per ounce).
        Teaches children whether buying a larger size actually saves money.
        """
        if self.unit_size > 0:
            return round(self.price / self.unit_size, 4)
        return 0.00
