from django.contrib import admin
from .building_blocks.bb_digital_registries.models import Registry


@admin.register(Registry)
class RegistryAdmin(admin.ModelAdmin):
    pass
