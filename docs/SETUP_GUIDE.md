# IshemaLink Setup & Deployment Guide

## Quick Start (Development)

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/ALU-BSE/adpy-26j-H3PHZY.git
cd adpy-26j-H3PHZY

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Initialization

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

### 3. Load Sample Data (Optional)

```bash
# Create Rwanda locations
python manage.py shell
>>> from core.models import Location
>>> # Create Districts and Sectors
>>> kigali = Location.objects.create(name="Kigali", location_type="DISTRICT", code="RW-01")
>>> gasabo = Location.objects.create(name="Gasabo", location_type="SECTOR", parent=kigali, code="RW-01-01")

# Create pricing zones and tariffs
python manage.py shell
>>> from billing.models import Zone, Tariff
>>> from decimal import Decimal
>>> zone1 = Zone.objects.create(zone_number=1, name="Zone 1 - Kigali", coverage_areas="Kigali City")
>>> Tariff.objects.create(
...   zone=zone1,
...   weight_from_kg=Decimal('0.1'),
...   weight_to_kg=Decimal('1.0'),
...   base_rate=Decimal('1500'),
...   per_kg_rate=Decimal('200')
... )
```

### 4. Run Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Access the API at `http://localhost:8000/api/`

---

## Docker Deployment

### 1. Build Docker Image

```bash
docker build -t ishemalink:latest .
```

### 2. Create docker-compose Configuration

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ishemalink
      POSTGRES_USER: ishemalink
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn ishemalink.wsgi:application --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key-here
      - DATABASE_URL=postgresql://ishemalink:secure_password@db:5432/ishemalink
    depends_on:
      - db
    volumes:
      - .:/code

volumes:
  postgres_data:
```

### 3. Deploy with Docker Compose

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## Production Deployment (Ubuntu 24.04)

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx gunicorn

# Create application user
sudo useradd -m -d /home/ishemalink ishemalink
sudo -u ishemalink mkdir -p /home/ishemalink/app
```

### 2. Application Setup

```bash
cd /home/ishemalink/app
sudo -u ishemalink git clone <repo> .
sudo -u ishemalink python3 -m venv venv
sudo -u ishemalink venv/bin/pip install -r requirements.txt

# Collect static files
sudo -u ishemalink venv/bin/python manage.py collectstatic --noinput

# Create database
sudo -u postgres psql -c "CREATE DATABASE ishemalink;"
sudo -u postgres psql -c "CREATE USER ishemalink_user WITH PASSWORD 'strong_password';"
sudo -u postgres psql -c "ALTER ROLE ishemalink_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ishemalink TO ishemalink_user;"
```

### 3. Gunicorn Configuration

Create `/home/ishemalink/app/gunicorn_config.py`:

```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
max_requests = 1000
timeout = 30
```

### 4. Systemd Service

Create `/etc/systemd/system/ishemalink.service`:

```ini
[Unit]
Description=IshemaLink API Service
After=network.target

[Service]
User=ishemalink
Group=www-data
WorkingDirectory=/home/ishemalink/app
Environment="PATH=/home/ishemalink/app/venv/bin"
ExecStart=/home/ishemalink/app/venv/bin/gunicorn \
    --config gunicorn_config.py \
    ishemalink.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ishemalink
sudo systemctl start ishemalink
```

### 5. Nginx Configuration

Create `/etc/nginx/sites-available/ishemalink`:

```nginx
upstream ishemalink {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.ishemalink.rw;

    client_max_body_size 100M;

    location /static/ {
        alias /home/ishemalink/app/staticfiles/;
    }

    location /media/ {
        alias /home/ishemalink/app/media/;
    }

    location / {
        proxy_pass http://ishemalink;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/ishemalink /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.ishemalink.rw
```

---

## Environment Variables

Create `.env` file:

```env
DEBUG=False
SECRET_KEY=your-secret-key-generate-with-django-shell
DATABASE_URL=postgresql://user:password@localhost:5432/ishemalink
ALLOWED_HOSTS=api.ishemalink.rw,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://api.ishemalink.rw

# Cache Configuration
CACHE_BACKEND=django.core.cache.backends.redis.RedisCache
CACHE_LOCATION=redis://127.0.0.1:6379/1

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery Configuration
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
```

---

## Testing & Monitoring

### Run Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test core

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Monitor Application

```bash
# Check service status
sudo systemctl status ishemalink

# View logs
sudo journalctl -u ishemalink -f

# Django debug
python manage.py shell
>>> from django.core.management import call_command
>>> call_command('check', '--deploy')
```

---

## Backup & Maintenance

### Database Backup

```bash
# PostgreSQL backup
sudo -u postgres pg_dump ishemalink > backup_$(date +%Y%m%d).sql

# Restore
sudo -u postgres psql ishemalink < backup_20260202.sql
```

### Log Rotation

Create `/etc/logrotate.d/ishemalink`:

```
/home/ishemalink/app/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 ishemalink www-data
}
```

---

## Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Enable HTTPS/SSL
- [ ] Set strong database passwords
- [ ] Configure CORS appropriately
- [ ] Enable CSRF protection
- [ ] Use environment variables for secrets
- [ ] Set up firewall rules
- [ ] Enable PostgreSQL authentication
- [ ] Configure rate limiting
- [ ] Set up monitoring/alerting

---

## Performance Tuning

### Database Optimization
```sql
-- Create indexes for common queries
CREATE INDEX idx_shipment_tracking ON domestic_shipment(tracking_number);
CREATE INDEX idx_shipment_status ON domestic_shipment(status);
CREATE INDEX idx_shipment_sender ON domestic_shipment(sender_id);
```

### Caching Strategy
- Tariffs: 24-hour cache
- Locations: 7-day cache
- User data: 1-hour cache

### Connection Pooling
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

---

## Support & Troubleshooting

### Common Issues

**Port 8000 already in use:**
```bash
sudo lsof -i :8000
sudo kill -9 <PID>
```

**Database connection error:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U ishemalink -d ishemalink
```

**Static files not serving:**
```bash
python manage.py collectstatic --clear --noinput
sudo systemctl restart ishemalink
```

For more support, check GitHub Issues or contact the development team.
