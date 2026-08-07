from django.contrib import admin
from users.models import FamilyGroup
from .models import Store, ShoppingTrip, ShoppingItem


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """
    Vendor location management registry.
    """
    list_display = ['name', 'address']
    search_fields = ['name', 'address']


class ShoppingItemInline(admin.TabularInline):
    """
    Enables embedded inline item editing directly inside a parent trip entry screen.
    This lets you add items and receipts on a single clean page.
    """
    model = ShoppingItem
    extra = 1
    fields = ['name', 'category', 'quantity', 'price', 'unit_type', 'unit_size', 'calculated_unit_price']
    readonly_fields = ['calculated_unit_price']

    def calculated_unit_price(self, obj):
        """Displays the calculated unit measurement price inside the inline row."""
        if obj.id:
            return f'${obj.cost_per_unit_measurement:.4f} per {obj.get_unit_type_display()}'
        return '_'
    calculated_unit_price.short_description = 'Educational Unit Price'


@admin.register(ShoppingTrip)
class ShoppingTripAdmin(admin.ModelAdmin):
    list_display = ('date', 'store', 'buyer', 'family_group', 'formatted_total_cost', 'is_completed')
    list_filter = ('is_completed', 'date', 'store', 'family_group')
    search_fields = ('store__name', 'buyer__username', 'family_group__name')
    date_hierarchy = 'date'
    inlines = [ShoppingItemInline]

    def formatted_total_cost(self, obj):
        return f"${obj.total_cost:.2f}"
    formatted_total_cost.short_description = 'Total Cost'

    # ADD THIS METHOD HERE TO FIX THE BLANK DROPDOWN
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Ensures the family group dropdown displays choices correctly in the admin view.
        """
        if db_field.name == "family_group":
            # If a superuser has no family group assigned yet, show all available family groups
            if request.user.is_superuser and not request.user.family_group:
                kwargs["queryset"] = FamilyGroup.objects.all()
            elif request.user.family_group:
                kwargs["queryset"] = FamilyGroup.objects.filter(id=request.user.family_group.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    """
    Granular product item audit registry for advanced cost reviews.
    """
    list_display = ('name', 'category', 'trip', 'quantity', 'formatted_price', 'unit_type', 'unit_size', 'educational_value')
    list_filter = ('category', 'unit_type', 'trip__date')
    search_fields = ('name', 'trip__store__name')

    def formatted_price(self, obj):
        return f"${obj.price:.2f}"
    formatted_price.short_description = 'Base Price'

    def educational_value(self, obj):
        """Displays breakdown strings mapping real unit cost dynamics."""
        return f"${obj.cost_per_unit_measurement:.4f} / {obj.unit_type}"
    educational_value.short_description = 'Unit Analytics'
