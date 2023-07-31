from django.contrib import admin
from .models import Registry


@admin.register(Registry)
class RegistryAdmin(admin.ModelAdmin):
    pass
