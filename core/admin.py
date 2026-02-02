from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Location


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Rwanda Info', {'fields': ('phone', 'national_id', 'user_type', 'assigned_sector')}),
        ('Status', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    list_display = ('username', 'email', 'phone', 'user_type', 'is_verified', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'phone', 'national_id')
    ordering = ('-created_at',)
    
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_type', 'parent', 'code')
    list_filter = ('location_type',)
    search_fields = ('name', 'code')
    ordering = ('name',)
