from django.contrib import admin
from .models import InternationalShipment, CustomsDocument


@admin.register(InternationalShipment)
class InternationalShipmentAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'sender', 'destination', 'status', 'customs_value', 'created_at')
    list_filter = ('destination', 'status', 'created_at')
    search_fields = ('tracking_number', 'sender_tin', 'recipient_tin')
    readonly_fields = ('tracking_number', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(CustomsDocument)
class CustomsDocumentAdmin(admin.ModelAdmin):
    list_display = ('declaration_number', 'intl_shipment', 'declared_value', 'destination_country')
    search_fields = ('declaration_number', 'intl_shipment__tracking_number')
    readonly_fields = ('created_at', 'updated_at')
