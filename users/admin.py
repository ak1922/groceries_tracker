from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AppUser, FamilyGroup

admin.site.register(AppUser)
admin.site.register(FamilyGroup)
