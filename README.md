[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/ecBgz8Pj)
[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=22400235)

# IshemaLink API - Rwanda Logistics Platform

A comprehensive Django REST Framework API for managing domestic and international shipments in Rwanda, with support for cross-border trade and real-time tracking.

## Project Overview

IshemaLink is a logistics platform connecting:
- **Domestic Courier**: Local delivery (Moto/Bus) across Rwanda's 30 Districts and 416 Sectors
- **International Cargo**: Cross-border trade with EAC partners (Kampala, Nairobi, Goma)
- **Customs Integration**: Strict documentation (TIN, Passport) for regulatory compliance

### Architecture

The project follows modular domain-driven design:

```
ishemalink/
├── core/                   # Shared utilities (User, Location, Validation)
├── domestic/               # Local delivery logic
├── international/          # Cross-border customs & documentation
├── billing/                # Pricing & tariff caching
├── ishemalink/             # Django project configuration
└── manage.py
```

## Task Implementations

### Task 1: Modular Project Architecture ✅
- **Logical Separation**: Distinct business flows for Domestic and International shipments
- **Environment Configuration**: `.env` for secret management
- **Git Repository**: Conventional commits with proper structure
- **API Documentation**: Basic routing and version endpoints

**Key Endpoints:**
- `GET /api/` - API root with version information
- `GET /api/status/` - System health check with database connectivity

### Task 2: Identity & Validation (Rwanda Context) ✅
- **Custom User Model**: `user_type` field (AGENT, CUSTOMER, ADMIN)
- **Rwanda Phone Validation**: Strict `+250 7XX XXX XXX` format
- **NID Validation**: 16-digit validation with type hints
- **Unit Tests**: Comprehensive validator tests

**Key Endpoints:**
- `POST /api/auth/register/` - User registration with validation
- `POST /api/auth/verify-nid/` - NID format verification
- `GET /api/users/me/` - Current user profile
- `POST /api/users/agents/onboard/` - Agent registration (requires NID)

### Task 3: Async Notification & Tracking ✅
- **Non-blocking Status Updates**: Asynchronous shipment status processing
- **ShipmentLog Model**: Tracks all status changes with timestamps and locations
- **Bulk Updates**: Batch processing for multiple shipments
- **Error Handling**: Continues processing even if individual updates fail

**Key Endpoints:**
- `POST /api/shipments/{tracking_number}/update-status/` - Update shipment status
- `POST /api/shipments/batch-update/` - Batch update multiple shipments
- `GET /api/shipments/{tracking_number}/tracking/` - Full tracking history

### Task 4: Tariff Caching Strategy ✅
- **Cache Implementation**: Django Local Memory Cache with 24-hour TTL
- **Zone-based Pricing**: Zone 1 (Kigali), Zone 2 (Provinces), Zone 3 (EAC)
- **Cache Headers**: Includes cache hit indicators in response
- **Admin Invalidation**: Endpoint to force cache refresh

**Key Endpoints:**
- `GET /api/pricing/tariffs/` - Get tariffs (cached)
- `POST /api/pricing/calculate/` - Calculate cost for weight/destination
- `POST /api/pricing/admin/cache/clear-tariffs/` - Admin cache clear

### Task 5: Paginated Manifests ✅
- **Page-number Pagination**: 20 items per page (configurable)
- **Filter Support**: By status, destination, location
- **Search**: By tracking number, recipient name, TIN
- **Mobile-friendly**: Minimal payload responses

**Key Endpoints:**
- `GET /api/shipments/?page=1&size=20` - List with pagination
- `GET /api/shipments/?status=IN_TRANSIT&destination=Kampala` - Filtered list
- `GET /api/shipments/?search=TRK123456` - Search shipments

## Installation & Setup

### Prerequisites
- Python 3.10+
- Django 6.0+
- PostgreSQL (recommended) or SQLite
- **Redis** (for Celery tasks) or configure `CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND` in `.env`

> The project defaults to `redis://localhost:6379/0` for Celery, so start a Redis daemon or
> supply an alternative broker URL in your environment before running asynchronous
> workers.
### Local Development

1. **Clone Repository**
   ```bash
   git clone <repo>
   cd adpy-26j-H3PHZY
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

## API Documentation

### Authentication

The API uses Token Authentication. Include the token in headers:

```bash
Authorization: Token <your-token>
```

### User Registration Example

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "agent_001",
    "email": "agent@ishemalink.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123",
    "phone": "+250788123456",
    "user_type": "AGENT",
    "assigned_sector": "Kicukiro/Niboye",
    "national_id": "1234567890123456"
  }'
```

### NID Verification

```bash
curl -X POST http://localhost:8000/api/auth/verify-nid/ \
  -H "Content-Type: application/json" \
  -d '{"nid": "1234567890123456"}'
```

### Create Shipment

```bash
curl -X POST http://localhost:8000/api/shipments/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_name": "John Doe",
    "recipient_phone": "+250799123456",
    "origin_location_id": 1,
    "destination_location_id": 2,
    "weight_kg": 5.5,
    "description": "Electronics shipment"
  }'
```

### Track Shipment

```bash
curl -X GET "http://localhost:8000/api/shipments/RW-ABC12345/tracking/" \
  -H "Authorization: Token <token>"
```

## Docker Deployment

### Build & Run with Docker

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000/`

### Environment Variables (Docker)

Set in `docker-compose.yml`:
```yaml
environment:
  - DEBUG=False
  - SECRET_KEY=your-secret-key
  - DATABASE_URL=postgresql://user:password@db:5432/ishemalink
```

## Testing

### Run All Tests

```bash
python manage.py test
```

### Run Specific App Tests

```bash
python manage.py test core
python manage.py test domestic
python manage.py test international
```

### Test with Coverage

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## Validation Rules

### Rwanda Phone Numbers
- **Format**: `+250 7XX XXX XXX`
- **Examples**: `+250788123456`, `+250799654321`
- **Validation**: Regex pattern `^\+2507\d{8}$`

### Rwanda National ID (NID)
- **Length**: 16 digits
- **Starting Digit**: 1-9 (not 0)
- **Validation**: Regex pattern `^[1-9]\d{15}$`
- **Examples**: `1234567890123456`, `9876543210987654`

## Performance Considerations

### Caching Strategy
- **Tariffs**: 24-hour cache TTL
- **Locations**: Loaded on startup
- **Cache Backend**: Django Local Memory Cache (LocMemCache)

### Database Optimizations
- **Indexes**: On frequently queried fields (tracking_number, status, sender)
- **Pagination**: Default 20 items per page
- **Query Optimization**: Select_related for foreign keys

### Async Processing
- Current implementation: Synchronous with error handling
- Future: Celery + Redis for true async task queue

## Code Structure

### Models

**Core App**
- `User`: Custom user model with Rwanda validation
- `Location`: Districts and Sectors hierarchy

**Domestic App**
- `Shipment`: Domestic shipment tracking
- `ShipmentLog`: Status change history

**International App**
- `InternationalShipment`: Cross-border shipments
- `CustomsDocument`: Customs declaration records

**Billing App**
- `Zone`: Geographic zones for pricing
- `Tariff`: Weight-based pricing rules
- `PriceHistory`: Audit trail for price changes

### Validators

```python
# validators.py
def validate_rwanda_phone(phone: str) -> Tuple[bool, str]
def validate_rwanda_nid(nid: str) -> Tuple[bool, str]
```

## Reflection: Domestic vs International Validation

The distinction between Domestic and International shipment validation reflects Rwanda's compliance requirements:

**Domestic Validation**:
- Focuses on internal routing within Rwanda's 30 districts
- Minimal documentation (phone, location)
- Fast processing for local courier services
- Lightweight payload for mobile connectivity in rural areas

**International Validation**:
- Requires strict customs documentation (TIN, Passport, HS codes)
- Customs value declaration mandatory
- Complex status tracking (Cleared Rwanda Customs → In Transit → Cleared Destination Customs)
- Compliance with EAC rules for Kampala, Nairobi, Goma

Key Implementation Details:
1. **Phone Validation** identical for both (Rwanda standard +250 7XX)
2. **NID Required** only for International shipments and Agent accounts
3. **Customs Doc** model exclusively for international (declaration numbers, origin/destination countries)
4. **Status Enums** different (IN_TRANSIT vs IN_TRANSIT + CLEARED_CUSTOMS_*)
5. **Cost Calculation** uses different tariffs (Zone-based vs destination-based)

This modular approach ensures Rwanda's KYC regulations are met while optimizing for fast domestic delivery and regulatory compliance for regional trade.

## Future Enhancements

1. **Celery Integration**: Real async task queue for notifications
2. **SMS Gateway**: Actual SMS notifications for status updates
3. **Mobile App**: React Native app for field agents
4. **Advanced Analytics**: Shipment trends and performance metrics
5. **Multi-currency Support**: For EAC regional pricing
6. **AI-based Routing**: Optimized delivery routes

## Support & Documentation

- **API Docs**: Postman collection available in `/docs/IshemaLink_Collection.json`
- **Django Admin**: `/admin/` for model management
- **Issue Tracking**: GitHub Issues for bug reports and feature requests

## License

This project is part of an academic assignment for ALU-BSE (African Leadership University).

---

**Last Updated**: February 2, 2026  
**Version**: 1.0.0  
**Status**: Active Development
