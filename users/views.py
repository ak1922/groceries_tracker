from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import FamilySignUpForm
from .models import FamilyGroup
from .tasks import send_registration_email


def register_view(request):
    if request.method == 'POST':
        form = FamilySignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')
            family_name = form.cleaned_data.get('new_family_name')

            # Links the family group bucket if they are a Head of Family
            if role == 'HEAD' and family_name:
                group, _ = FamilyGroup.objects.get_or_create(name=family_name)
                user.family_group = group

            send_registration_email.delay(user.email, user.username)

            user.save()

            messages.success(
                request,
                f"Account successfully provisioned! Welcome to GroceryOps, {user.username}. Your household cluster is ready."
            )

            # Log the user into their session automatically.
            login(request, user, backend='users.backends.EmailOrUsernameBackend')
            return redirect('shopping:dashboard')
    else:
        form = FamilySignUpForm()
    return render(request, 'users/register.html', {'form': form})
