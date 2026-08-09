from django import forms
from .models import Store, ShoppingTrip, ShoppingItem
from django.utils import timezone


class StoreCreateForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'store_type', 'address', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Trader Joe\'s'}),
            'store_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123 Main St'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '2', 'placeholder': 'Add custom store notes...'}),
        }


    def clean_name(self):
        """Enforces clean, non-empty, unique store naming boundaries."""
        name = self.cleaned_data.get('name').strip()
        if not name:
            raise forms.ValidationError('Store name cannot be left blank.')

        if Store.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError(f"A vendor named '{name}' is already registered.")
        return name


class ShoppingTripForm(forms.ModelForm):
    class Meta:
        model = ShoppingTrip
        fields = ['store', 'date']
        widgets = {
            'store': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }

        def clean_date(self):
            """Prevents logging grocery shopping trips with futuristic dates."""
            purchase_date = self.cleaned_data.get('date')
            if purchase_date and purchase_date > timezone.now().date():
                raise forms.ValidationError('You cannot log a shopping trip for a future date.')
            return purchase_date


class ShoppingItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingItem
        fields = ['name', 'category', 'price', 'quantity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Item name'}),
            'brand': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'e.g., Great Value'}),
            'category': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'price': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.01', 'placeholder': '0.00'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': '1'}),
            'is_essential': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Grocery item name cannot be empty.")
        return name

    def clean_price(self):
        """Guarantees financial cost fields are strictly positive numbers."""
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Item unit price must be a positive number greater than zero.")
        return price

    def clean_quantity(self):
        """Enforces that item quantities are integers greater than zero."""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 1:
            raise forms.ValidationError("Item count quantity must be at least 1 unit.")
        return quantity
