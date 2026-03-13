from django.contrib import admin
from .models import Zone, Tariff, PriceHistory


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('zone_number', 'name', 'coverage_areas')
    ordering = ('zone_number',)


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('zone', 'weight_from_kg', 'weight_to_kg', 'base_rate', 'per_kg_rate', 'active')
    list_filter = ('zone', 'active')
    ordering = ('zone', 'weight_from_kg')


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('tariff', 'old_base_rate', 'new_base_rate', 'changed_by', 'changed_at')
    list_filter = ('changed_at',)
    search_fields = ('tariff__zone__name',)
    readonly_fields = ('changed_at',)
    ordering = ('-changed_at',)
