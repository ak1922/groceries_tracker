from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

AppUser = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend allowing dual email or username logins.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Query against both username and email parameters seamlessly
            user = AppUser.objects.get(Q(username=username) | Q(email=username))
        except AppUser.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
