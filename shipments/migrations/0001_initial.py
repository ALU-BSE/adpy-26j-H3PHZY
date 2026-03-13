# Generated migration for shipments app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tracking_code', models.CharField(max_length=30, unique=True)),
                ('tariff', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(choices=[('PENDING_PAYMENT', 'Pending payment'), ('PAID', 'Paid'), ('DISPATCHED', 'Dispatched'), ('FAILED', 'Failed')], default='PENDING_PAYMENT', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('destination', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shipments_destination', to='core.location')),
                ('driver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_shipments', to=settings.AUTH_USER_MODEL)),
                ('origin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shipments_origin', to='core.location')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='shipment',
            index=models.Index(fields=['tracking_code'], name='shipments_s_trackin_idx'),
        ),
        migrations.AddIndex(
            model_name='shipment',
            index=models.Index(fields=['status'], name='shipments_s_status_idx'),
        ),
    ]
