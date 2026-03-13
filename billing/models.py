from django.db import models
from decimal import Decimal


class Zone(models.Model):
    """Shipping zones in Rwanda and neighboring countries"""
    ZONE_CHOICES = (
        (1, 'Zone 1 - Kigali'),
        (2, 'Zone 2 - Provinces'),
        (3, 'Zone 3 - EAC'),
    )
    
    zone_number = models.IntegerField(choices=ZONE_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    coverage_areas = models.TextField(help_text="Comma-separated list of covered areas")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['zone_number']
    
    def __str__(self):
        return self.name


class Tariff(models.Model):
    """Shipping tariffs by zone and weight"""
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='tariffs')
    
    weight_from_kg = models.DecimalField(max_digits=8, decimal_places=2)
    weight_to_kg = models.DecimalField(max_digits=8, decimal_places=2)
    
    base_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base rate in RWF")
    per_kg_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Rate per additional kg in RWF")
    
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('zone', 'weight_from_kg', 'weight_to_kg')
        ordering = ['zone', 'weight_from_kg']
    
    def __str__(self):
        return f"Zone {self.zone.zone_number}: {self.weight_from_kg}-{self.weight_to_kg}kg"
    
    def calculate_cost(self, weight_kg: Decimal) -> Decimal:
        """Calculate cost for given weight"""
        if weight_kg <= 1:
            return self.base_rate
        
        excess_weight = weight_kg - 1
        return self.base_rate + (excess_weight * self.per_kg_rate)


class PriceHistory(models.Model):
    """Track price changes for auditing"""
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, related_name='history')
    
    old_base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    new_base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    old_per_kg_rate = models.DecimalField(max_digits=10, decimal_places=2)
    new_per_kg_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    changed_by = models.CharField(max_length=255)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"Price change for {self.tariff} on {self.changed_at}"
