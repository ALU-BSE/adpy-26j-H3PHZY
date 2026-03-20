from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Tariff, Zone

@receiver([post_save, post_delete], sender=Tariff)
def invalidate_tariff_cache(sender, instance, **kwargs):
    """Invalidate tariff cache when a Tariff is saved or deleted"""
    cache.delete('tariffs_list')
    print(f"Tariff cache invalidated due to change in {instance}")

@receiver([post_save, post_delete], sender=Zone)
def invalidate_zone_cache(sender, instance, **kwargs):
    """Invalidate tariff cache when a Zone is saved or deleted"""
    cache.delete('tariffs_list')
    print(f"Tariff cache invalidated due to change in {instance}")
