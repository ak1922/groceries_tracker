from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from .managers import ShoppingTripQuerySet


class Store(models.Model):

    class StoreTypes(models.TextChoices):
        GROCERY = 'GROCERY', 'Supermarket / Grocery'
        WHOLESALE = 'WHOLESALE', 'Wholesale Club (Costco/Sam\'s)'
        CONVENIENCE = 'CONVENIENCE', 'Convenience Store'
        FARMERS = 'FARMERS', 'Farmers Market / Local Vendor'

    name = models.CharField(max_length=100)
    store_type = models.CharField(max_length=20, choices=StoreTypes.choices, default=StoreTypes.GROCERY)
    address = models.CharField(max_length=255, blank=True, help_text="e.g., 123 Main St")
    notes = models.TextField(blank=True, help_text="Store specific details (e.g., best place for bulk meat)")

    def __str__(self):
        return f'{self.name} ({self.get_store_type_display()})'


class ShoppingTrip(models.Model):
    family_group = models.ForeignKey('users.FamilyGroup', on_delete=models.CASCADE, related_name='trips')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='trips_logged')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='trips')
    date = models.DateField(default=timezone.now)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    budget_alert_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text='Target spending limit for this specific trip')
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
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], help_text='Price per single unit container')
    unit_type = models.CharField(max_length=3, choices=UnitTypes.choices, default=UnitTypes.PIECE)
    unit_size = models.DecimalField(max_digits=6, decimal_places=2, default=1.00, help_text="e.g., enter 16.00 for a 16oz cereal box")
    brand = models.CharField(max_length=100, blank=True, help_text="e.g., Kirkland, Organic Valley")
    is_essential = models.BooleanField(default=True, help_text="Uncheck for luxury/impulse purchases")

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
