# IshemaLink - File Structure & Purpose Guide

## Project Root Files

### Configuration & Setup
- **`manage.py`** - Django command-line utility
- **`requirements.txt`** - Python dependencies list
- **`Dockerfile`** - Docker image configuration
- **`docker-compose.yml`** - Docker Compose orchestration
- **`.env.example`** - Environment variables template
- **`.gitignore`** - Git ignore patterns

### Documentation (Root Level)
- **`README.md`** - Complete API documentation and setup guide
- **`COMPLETION_SUMMARY.md`** - Project completion summary
- **`IMPLEMENTATION_CHECKLIST.md`** - Detailed task checklist
- **`test_api.sh`** - Bash script for testing API endpoints

---

## `ishemalink/` - Django Project Configuration

### Core Configuration Files
- **`settings.py`** - Django settings
  - Database configuration
  - Installed apps (core, domestic, international, billing)
  - REST Framework settings
  - Cache configuration
  - CORS settings
  - Custom User model setup

- **`urls.py`** - Main URL router
  - Health check endpoint: `/api/status/`
  - API root: `/api/`
  - Includes routes from all apps

- **`wsgi.py`** - WSGI application entry point
- **`asgi.py`** - ASGI application entry point
- **`__init__.py`** - Package initialization

---

## `core/` - User Authentication & Validation

### Application Files
- **`models.py`** - Core models
  - `User` - Custom user model with Rwanda validation
  - `Location` - District/Sector hierarchy

- **`views.py`** - API views
  - `HealthCheckView` - System health endpoint
  - `APIRootView` - API root information
  - `UserRegistrationView` - User registration
  - `NIDBatchVerificationView` - NID verification
  - `UserProfileView` - Current user profile
  - `AgentOnboardingView` - Agent-specific registration

- **`serializers.py`** - DRF serializers
  - `UserSerializer` - User data serialization
  - `UserRegistrationSerializer` - Registration validation
  - `UserProfileSerializer` - Profile data
  - `NIDBatchVerificationSerializer` - NID verification

- **`validators.py`** - Rwanda-specific validators
  - `validate_rwanda_phone()` - Phone format validation
  - `validate_rwanda_nid()` - NID format validation
  - Quick boolean versions for efficient checks

- **`admin.py`** - Django admin interface
  - User admin with Rwanda-specific fields
  - Location admin with hierarchy display

- **`urls.py`** - App URL routing
  - Registration: `POST /api/auth/register/`
  - NID verification: `POST /api/auth/verify-nid/`
  - User profile: `GET /api/users/me/`
  - Agent onboarding: `POST /api/users/agents/onboard/`

### Test Files
- **`test_validators.py`** - Validator unit tests
  - 3 test classes, 6 test methods
  - Valid/invalid phone testing
  - Valid/invalid NID testing
  - Quick validation testing

- **`test_api.py`** - API endpoint tests
  - 3 test classes, 7+ test methods
  - User registration tests
  - NID verification tests
  - Health check tests

- **`migrations/`** - Database migrations
  - `0001_initial.py` - Initial User and Location models

---

## `domestic/` - Local Courier Management

### Application Files
- **`models.py`** - Domestic shipment models
  - `Shipment` - Domestic shipment tracking
    - Tracking number, sender, recipient
    - Origin/destination locations
    - Weight, description, status, cost
  - `ShipmentLog` - Status change history
    - Tracks every status update with timestamp
    - Location and notes
    - Indexed for performance

- **`views.py`** - Domestic shipment views
  - `ShipmentListCreateView` - List and create shipments
  - `ShipmentDetailView` - Retrieve/update details
  - `ShipmentTrackingView` - Get tracking history
  - `ShipmentStatusUpdateView` - Update status (async-ready)
  - `ShipmentBatchUpdateView` - Batch process updates

- **`serializers.py`** - Shipment serializers
  - `ShipmentLogSerializer` - Log entries
  - `ShipmentSerializer` - Full shipment data
  - `ShipmentCreateSerializer` - Creation with auto-ID
  - `ShipmentStatusUpdateSerializer` - Status update validation

- **`admin.py`** - Django admin interface
  - Shipment admin with status filtering
  - ShipmentLog admin with timeline display

- **`urls.py`** - Domestic URL routing
  - List/create: `GET/POST /api/shipments/`
  - Detail: `GET/PUT /api/shipments/{tracking}/`
  - Tracking: `GET /api/shipments/{tracking}/tracking/`
  - Status update: `POST /api/shipments/{tracking}/update-status/`
  - Batch update: `POST /api/shipments/batch-update/`

- **`migrations/`** - Database migrations
  - `0001_initial.py` - Initial Shipment models with indexes

---

## `international/` - Cross-Border Trade

### Application Files
- **`models.py`** - International shipment models
  - `InternationalShipment` - Cross-border shipment
    - All Domestic fields PLUS customs fields
    - sender_tin, recipient_passport, recipient_tin
    - hs_code, customs_value
    - Destination (KAMPALA, NAIROBI, GOMA, BUJUMBURA)
  - `CustomsDocument` - Customs declaration
    - declaration_number (unique)
    - declared_value, origin/destination countries

- **`views.py`** - International shipment views
  - `InternationalShipmentListCreateView` - List/create
  - `InternationalShipmentDetailView` - Detail view
  - `InternationalShipmentTrackingView` - Tracking with customs

- **`serializers.py`** - International serializers
  - `CustomsDocumentSerializer` - Customs data
  - `InternationalShipmentSerializer` - Full shipment
  - `InternationalShipmentCreateSerializer` - Creation with auto-generation

- **`admin.py`** - Django admin interface
  - InternationalShipment admin with destination filtering
  - CustomsDocument admin

- **`urls.py`** - International URL routing
  - List/create: `GET/POST /api/international/shipments/`
  - Detail: `GET/PUT /api/international/shipments/{tracking}/`
  - Tracking: `GET /api/international/shipments/{tracking}/tracking/`

- **`migrations/`** - Database migrations
  - `0001_initial.py` - Initial international models

---

## `billing/` - Pricing & Tariffs

### Application Files
- **`models.py`** - Pricing models
  - `Zone` - Geographic zones (3 zones)
    - zone_number (1=Kigali, 2=Provinces, 3=EAC)
    - name, description, coverage_areas
  - `Tariff` - Weight-based pricing
    - zone, weight range
    - base_rate, per_kg_rate
  - `PriceHistory` - Audit trail
    - Old/new rates, changed_by, timestamp

- **`views.py`** - Pricing views
  - `TariffListView` - Get tariffs (cached, 24-hour TTL)
  - `ZoneListView` - List zones
  - `PricingCalculateView` - Calculate cost
  - `CacheClearView` - Admin: clear cache

- **`serializers.py`** - Pricing serializers
  - `TariffSerializer` - Tariff data
  - `ZoneSerializer` - Zone with tariffs
  - `PricingCalculatorSerializer` - Cost calculation

- **`admin.py`** - Django admin interface
  - Zone admin
  - Tariff admin with active/inactive filtering
  - PriceHistory admin with audit trail

- **`urls.py`** - Billing URL routing
  - Tariffs: `GET /api/pricing/tariffs/`
  - Zones: `GET /api/pricing/zones/`
  - Calculate: `POST /api/pricing/calculate/`
  - Cache clear: `POST /api/pricing/admin/cache/clear-tariffs/`

- **`migrations/`** - Database migrations
  - `0001_initial.py` - Initial pricing models

---

## `docs/` - Documentation

### API Documentation
- **`IshemaLink_Collection.json`** - Postman API collection
  - 5 folders of endpoints
  - 20+ example requests
  - Ready to import and test

### Setup & Deployment
- **`SETUP_GUIDE.md`** - Complete deployment guide
  - Local development setup
  - Docker deployment
  - Production deployment (Ubuntu 24.04)
  - Environment configuration
  - Backup and maintenance procedures

### Analysis & Reflection
- **`REFLECTION.md`** - Design analysis (300+ words)
  - Domestic vs International validation
  - Regulatory alignment
  - User experience impact
  - Technical implementation details

### Project Documentation
- **`PROJECT_SUMMARY.md`** - Technical overview
  - Task completion details
  - API response examples
  - Technology stack
  - Testing strategy
  - Future enhancements

---

## Database Migrations

### Created Migrations
```
core/migrations/
  0001_initial.py          - User and Location models

domestic/migrations/
  0001_initial.py          - Shipment and ShipmentLog models

international/migrations/
  0001_initial.py          - International and Customs models

billing/migrations/
  0001_initial.py          - Zone, Tariff, PriceHistory models
```

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Python Modules** | 30+ |
| **Models** | 9 |
| **Views/ViewSets** | 13 |
| **Serializers** | 10+ |
| **API Endpoints** | 18 |
| **Test Classes** | 5 |
| **Test Methods** | 13+ |
| **Admin Classes** | 8 |
| **URL Patterns** | 16 |
| **Doc Files** | 7 |

---

## Code Organization Best Practices

✅ **Separation of Concerns**
- Models for data
- Views for business logic
- Serializers for API representation
- Validators for input validation

✅ **Type Hints**
- All validator functions typed
- Function signatures documented
- Return types specified

✅ **Documentation**
- Docstrings on classes and methods
- Comments on complex logic
- README for overview
- Postman collection for examples

✅ **Testing**
- Unit tests for validators
- API endpoint tests
- Test discovery configured
- >80% code coverage goal

✅ **Security**
- Input validation
- Token authentication
- CSRF protection
- Permission checks

---

## File Access Patterns

### Adding New Features
1. Create/modify `models.py`
2. Generate migrations: `python manage.py makemigrations`
3. Create `serializers.py` for API representation
4. Create `views.py` with business logic
5. Add `urls.py` routes
6. Create `admin.py` interface
7. Write tests in `test_*.py`
8. Apply migrations: `python manage.py migrate`

### Testing
```bash
python manage.py test core.test_validators
python manage.py test core.test_api
coverage run --source='.' manage.py test
```

### Deployment
```bash
# Development
python manage.py runserver

# Docker
docker-compose up --build

# Production
See docs/SETUP_GUIDE.md
```

---

## Key File Relationships

```
Settings.py
  ├── Specifies AUTH_USER_MODEL → core.User
  ├── Includes all apps
  ├── REST Framework configuration
  └── Cache configuration

Main urls.py
  ├── Health endpoint
  ├── API root
  └── Include: core, domestic, international, billing urls

core/models.py (User)
  ├── Referenced by: domestic.Shipment (sender)
  ├── Referenced by: international.InternationalShipment (sender)
  └── Referenced by: ShipmentLog (logged_by)

core/models.py (Location)
  ├── Referenced by: domestic.Shipment (origin, destination)
  ├── Referenced by: international.InternationalShipment (origin)
  └── Referenced by: ShipmentLog (location)
```

---

**File Structure Last Updated**: February 2, 2026  
**Project Status**: ✅ Complete  
**Documentation Level**: Comprehensive
