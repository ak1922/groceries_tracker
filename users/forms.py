from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from .tasks import send_async_reset_email


AppUser = get_user_model()

class FamilySignUpForm(UserCreationForm):
    """
    Handles user creation fields along with family group allocation.
    """
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=AppUser.Roles.choices, required=True, widget=forms.Select(attrs={'class': 'form-select'}))
    new_family_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Provide a name only if you are registering as a Head of Family to create a new household bucket."
    )

    class Meta(UserCreationForm.Meta):
        model = AppUser
        fields = ('username', 'email', 'role')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if AppUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        family_name = cleaned_data.get('new_family_name')

        if role == 'HEAD' and not family_name:
            self.add_error('new_family_name', "A household cluster name is required for Head of Family accounts.")
        return cleaned_data


class DualAuthenticationForm(AuthenticationForm):
    """
    Custom login form that visually matches our Bootstrap design language
    and prompts users for either their username or email address.
    """
    username = forms.CharField(
        label="Username or Email Address",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username or email...'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )


class ProfileUpdateForm(forms.ModelForm):
    """
    Handles user profile edits and filters file type uploads safely.
    """
    class Meta:
        model = AppUser
        fields = ('username', 'email', 'profile_photo')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CeleryPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name = None,
    ):
        from django.template.loader import render_to_string

        body = render_to_string(email_template_name, context)
        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())

        send_async_reset_email.delay(subject, body, from_email, to_email)
