# IshemaLink Architecture

The IshemaLink API is built with a highly modular, domain-driven design that separates core logistics concerns into dedicated Django applications.

## High-Level Design

The project leverages Django REST Framework (DRF) for the API layer and Celery for asynchronous processing.

```mermaid
graph TD
    User((User)) --> API[DRF API Layer]
    API --> Core[core: Auth & Validation]
    API --> Domestic[domestic: Local Shipments]
    API --> International[international: Cross-border Cargo]
    
    Domestic --> NotifTask[notifications: Async SMS/Email Task]
    International --> NotifTask
    
    NotifTask --># IshemaLink National Rollout Architecture

This document details the enterprise architecture of IshemaLink to support 5,000+ concurrent users and mandatory GovTech integrations.

## System Architecture (Containers & Services)

```mermaid
graph TD
    User((User/Agent)) --> Nginx[Nginx Reverse Proxy]
    Nginx --> Gunicorn[Gunicorn/Django Web]
    Gunicorn --> DB[(PostgreSQL Main)]
    Gunicorn --> Redis[(Redis Cache/Queue)]
    Gunicorn --> GovAPI[External Gov APIs RRA/RURA]
    Redis --> Worker[Celery Worker]
    Worker --> Notify[Notification Services SMS/Email]
    
    subgraph "Rwanda Cloud Infrastructure"
        Gunicorn
        DB
        Redis
        Worker
    end
```

## Unified Booking Flow (Status Transitions)

The system uses a state machine to ensure ACID-compliant transactions across financial and cargo records.

```mermaid
state_diagram
    [*] --> PENDING_PAYMENT
    PENDING_PAYMENT --> PAID : Mobile Money Success
    PENDING_PAYMENT --> FAILED : Payment Timeout/Cancel
    PAID --> RURA_VERIFIED : Auto-License Check
    RURA_VERIFIED --> DISPATCHED : Driver Assigned
    DISPATCHED --> IN_TRANSIT
    IN_TRANSIT --> DELIVERED
```

## Component Breakdown

### 1. Core Integration Services
- **BookingService**: Orchestrates atomic transactions between shipments and payments.
- **GovTech Connectors**: (RRA, RURA) Ensure 100% tax compliance and transport authorization.

### 2. Performance & Scalability
- **Connection Pooling**: PgBouncer ensures efficient Postgres connection management.
- **Two-Tier Caching**: Local memory for static tariffs + Redis for global session/queue data.

### 3. Monitoring (Control Tower)
- **Prometheus/Grafana**: Tracks system saturation and request latencies.
- **Deep Health**: Real-time monitoring of DB, Redis, and disk availability.
 Celery[Celery Worker]
    Celery --> Redis[(Redis Broker)]
```

## Modular Components

- **`core`**: Contains the custom `User` model with Rwanda-specific KYC (NID/Phone) validation. It serves as the identity provider for the entire system.
- **`domestic`**: Manages shipments within Rwanda. It uses a location hierarchy to calculate costs and track movements.
- **`international`**: Handles cross-border trade, including customs documentation (TIN, Passport) and complex status tracking.
- **`notifications`**: A dedicated service app that handles all outbound communication. By offloading this to a separate app, we maintain high decoupling.
- **`billing`**: Manages the price engine and tariff caching strategy (24h TTL) to ensure high performance under load.

## Tech Stack

- **Framework**: Django 6.0 + Django REST Framework
- **Asynchronous Processing**: Celery + Redis
- **Database**: SQLite (Development) / PostgreSQL (Production ready)
- **Validation**: Custom Regex-based Rwanda identity validation
- **Documentation**: Swagger/OpenAPI & Postman
