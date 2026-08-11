from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Store
from ..forms import StoreCreateForm


@login_required
def store_list(request):
    stores = Store.objects.all().order_by('name')
    return render(request, 'shopping/store_list.html', {'stores': stores})


@login_required
def store_edit(request, pk):
    store = get_object_or_404(Store, id=pk)
    form = StoreCreateForm(request.POST or None, instance=store)

    if request.method == 'POST'  and form.is_valid():
        form.save()
        messages.success(request, f"Configuration modifications for '{store.name}' saved successfully.")
        return redirect('shopping:store_list')

    context = {
        'store': store,
        'form': form,
    }
    return render(request, 'shopping/store_form.html', context)


@login_required
def store_delete(request, pk):
    store = get_object_or_404(Store, id=pk)
    store_name = store.name

    if request.method == 'POST':
        store.delete()
        messages.success(request, f"Vendor destination '{store_name}' purged from network maps.")
        return redirect('shopping:store_list')
    return render(request, 'shopping/store_confirm_delete.html', {'store': store})
