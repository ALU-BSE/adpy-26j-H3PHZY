from django.contrib import admin
from .models import Shipment, ShipmentLog


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'sender', 'recipient_name', 'status', 'weight_kg', 'cost', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('tracking_number', 'recipient_name', 'sender__phone')
    readonly_fields = ('tracking_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(ShipmentLog)
class ShipmentLogAdmin(admin.ModelAdmin):
    list_display = ('shipment', 'status', 'location', 'logged_by', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('shipment__tracking_number', 'location__name')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
