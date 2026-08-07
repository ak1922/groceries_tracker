from django.contrib.auth.models import AbstractUser
from django.db import models


class FamilyGroup(models.Model):
    """
    Defines a unique household group. All shopping trips and monthly metrics
    are bound strictly to this group for multi-tenant data isolation.
    """
    name = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class AppUser(AbstractUser):
    """
    Custom user table implementing role privileges and family assignments.
    """
    class Roles(models.TextChoices):
        HEAD_OF_FAMILY = 'HEAD', 'Head of Family'
        FAMILY_MEMBER = 'MEMBER', 'Family Member'

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.FAMILY_MEMBER
    )
    family_group = models.ForeignKey(
        FamilyGroup,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='members'
    )
    profile_photo = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text='Upload a custom photo for your household avatar profile card.'
    )

    REQUIRED_FIELDS = ['email']

    def is_head(self):
        """Helper utility to check executive dashboard access capabilities."""
        return self.role == self.Roles.HEAD_OF_FAMILY
