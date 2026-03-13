"""Pytest configuration and shared fixtures for IshemaLink tests."""

import os
import django
from django.conf import settings

import pytest
from django.test import Client


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ishemalink.settings')
django.setup()


@pytest.fixture
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        pass


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!',
        phone='+250788123456',
        user_type='CUSTOMER'
    )


@pytest.fixture
def authenticated_api_client(db, authenticated_user):
    from rest_framework.test import APIClient
    client = APIClient()
    client.force_authenticate(user=authenticated_user)
    return client


@pytest.fixture
def test_locations(db):
    from core.models import Location
    origin = Location.objects.create(
        name='Kigali Central',
        location_type='SECTOR',
        code='KIG-001',
        latitude=-1.9536,
        longitude=29.8739
    )
    destination = Location.objects.create(
        name='Kigali Hub',
        location_type='SECTOR',
        code='KIG-002',
        latitude=-1.9500,
        longitude=29.8700
    )
    return {'origin': origin, 'destination': destination}


@pytest.fixture
def test_shipment(db, authenticated_user, test_locations):
    from shipments.models import Shipment
    return Shipment.objects.create(
        tracking_code='RW-TEST12345',
        sender=authenticated_user,
        origin=test_locations['origin'],
        destination=test_locations['destination'],
        tariff='50.00',
        status='PENDING_PAYMENT'
    )


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with Django settings."""
    config.addinivalue_line(
        "markers",
        "unit: Unit tests (non-DB)"
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests (database required)"
    )
    config.addinivalue_line(
        "markers",
        "slow: Slow tests"
    )


# pytest options
pytest_plugins = ("pytest_django",)
